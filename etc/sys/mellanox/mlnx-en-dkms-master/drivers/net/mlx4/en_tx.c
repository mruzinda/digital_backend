/*
 * Copyright (c) 2007 Mellanox Technologies. All rights reserved.
 *
 * This software is available to you under a choice of one of two
 * licenses.  You may choose to be licensed under the terms of the GNU
 * General Public License (GPL) Version 2, available from the file
 * COPYING in the main directory of this source tree, or the
 * OpenIB.org BSD license below:
 *
 *     Redistribution and use in source and binary forms, with or
 *     without modification, are permitted provided that the following
 *     conditions are met:
 *
 *      - Redistributions of source code must retain the above
 *        copyright notice, this list of conditions and the following
 *        disclaimer.
 *
 *      - Redistributions in binary form must reproduce the above
 *        copyright notice, this list of conditions and the following
 *        disclaimer in the documentation and/or other materials
 *        provided with the distribution.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 */

#include <asm/page.h>
#include <linux/mlx4/cq.h>
#include <linux/mlx4/qp.h>
#include <linux/skbuff.h>
#include <linux/if_vlan.h>
#include <linux/vmalloc.h>

#include "mlx4_en.h"

enum {
	MAX_INLINE = 104, /* 128 - 16 - 4 - 4 */
	MAX_BF = 256,
};

static int inline_thold __read_mostly = MAX_INLINE;

module_param_named(inline_thold, inline_thold, int, 0444);
MODULE_PARM_DESC(inline_thold, "treshold for using inline data");

int mlx4_en_create_tx_ring(struct mlx4_en_priv *priv,
			   struct mlx4_en_tx_ring *ring, int qpn, u32 size,
			   u16 stride)
{
	struct mlx4_en_dev *mdev = priv->mdev;
	int tmp;
	int err;

	ring->size = size;
	ring->size_mask = size - 1;
	ring->stride = stride;
	ring->full_size = ring->size - HEADROOM - MAX_DESC_TXBBS;

	inline_thold = min(inline_thold, MAX_INLINE);

	spin_lock_init(&ring->comp_lock);

	tmp = size * sizeof(struct mlx4_en_tx_info);
	ring->tx_info = vmalloc_node(tmp, ring->numa_node);
	if (!ring->tx_info) {
		en_err(priv, "Failed allocating tx_info ring\n");
		return -ENOMEM;
	}
	en_dbg(DRV, priv, "Allocated tx_info ring at addr:%p size:%d\n",
		 ring->tx_info, tmp);

	ring->bounce_buf = kmalloc_node(MAX_DESC_SIZE, GFP_KERNEL, ring->numa_node);
	if (!ring->bounce_buf)
		ring->bounce_buf = kmalloc(MAX_DESC_SIZE, GFP_KERNEL);
	if (!ring->bounce_buf) {
		en_err(priv, "Failed allocating bounce buffer\n");
		err = -ENOMEM;
		goto err_tx;
	}
	ring->buf_size = ALIGN(size * ring->stride, MLX4_EN_PAGE_SIZE);

	err = mlx4_alloc_hwq_res(mdev->dev, &ring->wqres, ring->buf_size,
				 2 * PAGE_SIZE, ring->numa_node);
	if (err) {
		en_err(priv, "Failed allocating hwq resources\n");
		goto err_bounce;
	}

	err = mlx4_en_map_buffer(&ring->wqres.buf, ring->numa_node);
	if (err) {
		en_err(priv, "Failed to map TX buffer\n");
		goto err_hwq_res;
	}

	ring->buf = ring->wqres.buf.direct.buf;

	en_dbg(DRV, priv, "Allocated TX ring (addr:%p) - buf:%p size:%d "
	       "buf_size:%d dma:%llx\n", ring, ring->buf, ring->size,
	       ring->buf_size, (unsigned long long) ring->wqres.buf.direct.map);

	ring->qpn = qpn;
	err = mlx4_qp_alloc(mdev->dev, ring->qpn, &ring->qp);
	if (err) {
		en_err(priv, "Failed allocating qp %d\n", ring->qpn);
		goto err_map;
	}
	ring->qp.event = mlx4_en_sqp_event;

	err = mlx4_bf_alloc(mdev->dev, &ring->bf, ring->numa_node);
	if (err) {
		en_dbg(DRV, priv, "working without blueflame (%d)", err);
		ring->bf.uar = &mdev->priv_uar;
		ring->bf.uar->map = mdev->uar_map;
		ring->bf_enabled = false;
	} else
		ring->bf_enabled = true;

	return 0;

err_map:
	mlx4_en_unmap_buffer(&ring->wqres.buf);
err_hwq_res:
	mlx4_free_hwq_res(mdev->dev, &ring->wqres, ring->buf_size);
err_bounce:
	kfree(ring->bounce_buf);
	ring->bounce_buf = NULL;
err_tx:
	vfree(ring->tx_info);
	ring->tx_info = NULL;
	return err;
}

void mlx4_en_destroy_tx_ring(struct mlx4_en_priv *priv,
			     struct mlx4_en_tx_ring *ring)
{
	struct mlx4_en_dev *mdev = priv->mdev;
	en_dbg(DRV, priv, "Destroying tx ring, qpn: %d\n", ring->qpn);

	if (ring->bf_enabled)
		mlx4_bf_free(mdev->dev, &ring->bf);
	mlx4_qp_remove(mdev->dev, &ring->qp);
	mlx4_qp_free(mdev->dev, &ring->qp);
	mlx4_en_unmap_buffer(&ring->wqres.buf);
	mlx4_free_hwq_res(mdev->dev, &ring->wqres, ring->buf_size);
	kfree(ring->bounce_buf);
	ring->bounce_buf = NULL;
	vfree(ring->tx_info);
	ring->tx_info = NULL;
}

int mlx4_en_activate_tx_ring(struct mlx4_en_priv *priv,
			     struct mlx4_en_tx_ring *ring,
			     int cq)
{
	struct mlx4_en_dev *mdev = priv->mdev;
	int err;

	ring->cqn = cq;
	ring->prod = 0;
	ring->cons = 0xffffffff;
	ring->last_nr_txbb = 1;
	ring->poll_cnt = 0;
	memset(ring->tx_info, 0, ring->size * sizeof(struct mlx4_en_tx_info));
	memset(ring->buf, 0, ring->buf_size);

	ring->qp_state = MLX4_QP_STATE_RST;
	ring->doorbell_qpn = ring->qp.qpn << 8;

	mlx4_en_fill_qp_context(priv, ring->size, ring->stride, 1, 0, ring->qpn,
				ring->cqn, &ring->context);
	if (ring->bf_enabled)
		ring->context.usr_page = cpu_to_be32(ring->bf.uar->index);

	err = mlx4_qp_to_ready(mdev->dev, &ring->wqres.mtt, &ring->context,
			       &ring->qp, &ring->qp_state);

	atomic_set(&ring->inflight, 0);
	return err;
}

void mlx4_en_deactivate_tx_ring(struct mlx4_en_priv *priv,
				struct mlx4_en_tx_ring *ring)
{
	struct mlx4_en_dev *mdev = priv->mdev;

	mlx4_qp_modify(mdev->dev, NULL, ring->qp_state,
		       MLX4_QP_STATE_RST, NULL, 0, 0, &ring->qp);
}


static u32 mlx4_en_free_tx_desc(struct mlx4_en_priv *priv,
				struct mlx4_en_tx_ring *ring,
				int index, u8 owner)
{
	struct mlx4_en_tx_info *tx_info = &ring->tx_info[index];
	struct mlx4_en_tx_desc *tx_desc = ring->buf + index * TXBB_SIZE;
	struct mlx4_wqe_data_seg *data = (void *) tx_desc + tx_info->data_offset;
	struct sk_buff *skb = tx_info->skb;
	struct skb_frag_struct *frag;
	void *end = ring->buf + ring->buf_size;
	int frags = skb_shinfo(skb)->nr_frags;
	int i;
	__be32 *ptr = (__be32 *)tx_desc;
	__be32 stamp = cpu_to_be32(STAMP_VAL | (!!owner << STAMP_SHIFT));

	/* Optimize the common case when there are no wraparounds */
	if (likely((void *) tx_desc + tx_info->nr_txbb * TXBB_SIZE <= end)) {
		if (!tx_info->inl) {
			if (tx_info->linear) {
				dma_unmap_single(priv->ddev,
					(dma_addr_t) be64_to_cpu(data->addr),
					 be32_to_cpu(data->byte_count),
					 PCI_DMA_TODEVICE);
				++data;
			}

			for (i = 0; i < frags; i++) {
				frag = &skb_shinfo(skb)->frags[i];
				dma_unmap_page(priv->ddev,
					(dma_addr_t) be64_to_cpu(data[i].addr),
					frag->size, PCI_DMA_TODEVICE);
			}
		}
		/* Stamp the freed descriptor */
		for (i = 0; i < tx_info->nr_txbb * TXBB_SIZE; i += STAMP_STRIDE) {
			*ptr = stamp;
			ptr += STAMP_DWORDS;
		}

	} else {
		if (!tx_info->inl) {
			if ((void *) data >= end) {
				data = (struct mlx4_wqe_data_seg *)
						(ring->buf + ((void *) data - end));
			}

			if (tx_info->linear) {
				dma_unmap_single(priv->ddev,
					(dma_addr_t) be64_to_cpu(data->addr),
					 be32_to_cpu(data->byte_count),
					 PCI_DMA_TODEVICE);
				++data;
			}

			for (i = 0; i < frags; i++) {
				/* Check for wraparound before unmapping */
				if ((void *) data >= end)
					data = (struct mlx4_wqe_data_seg *) ring->buf;
				frag = &skb_shinfo(skb)->frags[i];
				dma_unmap_page(priv->ddev,
					(dma_addr_t) be64_to_cpu(data->addr),
					 frag->size, PCI_DMA_TODEVICE);
				++data;
			}
		}
		/* Stamp the freed descriptor */
		for (i = 0; i < tx_info->nr_txbb * TXBB_SIZE; i += STAMP_STRIDE) {
			*ptr = stamp;
			ptr += STAMP_DWORDS;
			if ((void *) ptr >= end) {
				ptr = ring->buf;
				stamp ^= cpu_to_be32(0x80000000);
			}
		}

	}
	dev_kfree_skb_any(skb);
	return tx_info->nr_txbb;
}


int mlx4_en_free_tx_buf(struct net_device *dev, struct mlx4_en_tx_ring *ring)
{
	struct mlx4_en_priv *priv = netdev_priv(dev);
	int cnt = 0;

	/* Skip last polled descriptor */
	ring->cons += ring->last_nr_txbb;
	en_dbg(DRV, priv, "Freeing Tx buf - cons:0x%x prod:0x%x\n",
		 ring->cons, ring->prod);

	if ((u32) (ring->prod - ring->cons) > ring->size) {
		if (netif_msg_tx_err(priv))
			en_warn(priv, "Tx consumer passed producer!\n");
		return 0;
	}

	while (ring->cons != ring->prod) {
		ring->last_nr_txbb = mlx4_en_free_tx_desc(priv, ring,
						ring->cons & ring->size_mask,
						!!(ring->cons & ring->size));
		ring->cons += ring->last_nr_txbb;
		cnt++;
	}

	if (cnt)
		en_dbg(DRV, priv, "Freed %d uncompleted tx descriptors\n", cnt);

	return cnt;
}

void mlx4_en_set_prio_map(struct mlx4_en_priv *priv, u16 *prio_map, u32 ring_num)
{
	int block = 8 / ring_num;
	int extra = 8 - (block * ring_num);
	int num = 0;
	u16 ring = 1;
	int prio;

	if (ring_num == 1) {
		for (prio = 0; prio < 8; prio++)
			prio_map[prio] = 0;
		return;
	}

	for (prio = 0; prio < 8; prio++) {
		if (extra && (num == block + 1)) {
			ring++;
			num = 0;
			extra--;
		} else if (!extra && (num == block)) {
			ring++;
			num = 0;
		}
		prio_map[prio] = ring;
		en_dbg(DRV, priv, " prio:%d --> ring:%d\n", prio, ring);
		num++;
	}
}

static int mlx4_en_process_tx_cq(struct net_device *dev, struct mlx4_en_cq *cq, int budget)
{
	struct mlx4_en_priv *priv = netdev_priv(dev);
	struct mlx4_cq *mcq = &cq->mcq;
	struct mlx4_en_tx_ring *ring = priv->tx_ring[cq->ring];
	struct mlx4_cqe *cqe;
	u16 index;
	u16 new_index, ring_index;
	u32 txbbs_skipped = 0;
	int factor = priv->cqe_factor;
	u32 cons_index = mcq->cons_index;
	int size = cq->size;
	u32 size_mask = ring->size_mask;
	struct mlx4_cqe *buf = cq->buf;
	int done = 0;

	if (!priv->port_up)
		return 0;

	index = cons_index & size_mask;
	cqe = &buf[(index << factor) + factor];
	ring_index = ring->cons & size_mask;

	/* Process all completed CQEs */
	while (XNOR(cqe->owner_sr_opcode & MLX4_CQE_OWNER_MASK,
			cons_index & size) && (done < budget)) {
		/*
		 * make sure we read the CQE after we read the
		 * ownership bit
		 */
		rmb();

		/* Skip over last polled CQE */
		new_index = be16_to_cpu(cqe->wqe_index) & size_mask;

		do {
			txbbs_skipped += ring->last_nr_txbb;
			ring_index = (ring_index + ring->last_nr_txbb) & size_mask;
			/* free next descriptor */
			ring->last_nr_txbb = mlx4_en_free_tx_desc(
					priv, ring, ring_index,
					!!((ring->cons + txbbs_skipped) &
							ring->size));
		} while ((++done < budget) && (ring_index != new_index));

		++cons_index;
		index = cons_index & size_mask;
		cqe = &buf[(index << factor) + factor];
	}


	/*
	 * To prevent CQ overflow we first update CQ consumer and only then
	 * the ring consumer.
	 */
	mcq->cons_index = cons_index;
	mlx4_cq_set_ci(mcq);
	wmb();
	ring->cons += txbbs_skipped;
	atomic_sub(txbbs_skipped, &ring->inflight);

	/* Wakeup Tx queue if this ring stopped it */
	if (netif_tx_queue_stopped(netdev_get_tx_queue(dev, cq->ring)) &&
				   txbbs_skipped > 0) {
		netif_tx_wake_queue(netdev_get_tx_queue(dev, cq->ring));
		ring->wake_queue++;
	}
	return done;
}

void mlx4_en_tx_irq(struct mlx4_cq *mcq)
{
	struct mlx4_en_cq *cq = container_of(mcq, struct mlx4_en_cq, mcq);
	struct mlx4_en_priv *priv = netdev_priv(cq->dev);

	if (priv->port_up)
		napi_schedule(&cq->napi);
	else
		mlx4_en_arm_cq(priv, cq);
}

/* TX CQ polling - called by NAPI */
int mlx4_en_poll_tx_cq(struct napi_struct *napi, int budget)
{
	struct mlx4_en_cq *cq = container_of(napi, struct mlx4_en_cq, napi);
	struct net_device *dev = cq->dev;
	struct mlx4_en_priv *priv = netdev_priv(dev);
	int done;

	done = mlx4_en_process_tx_cq(dev, cq, budget);

	/* If we used up all the quota - we're probably not done yet... */
	if (done < budget) {
		/* Done for now */
		napi_complete(napi);
		mlx4_en_arm_cq(priv, cq);
		return done;
	}
	return budget;
}

static struct mlx4_en_tx_desc*
mlx4_en_bounce_to_desc(struct mlx4_en_tx_ring *ring, u32 index,
		       unsigned int desc_size)
{
	u32 copy = (ring->size - index) * TXBB_SIZE;
	int i;

	for (i = desc_size - copy - 4; i >= 0; i -= 4) {
		if ((i & (TXBB_SIZE - 1)) == 0)
			wmb();

		*((u32 *) (ring->buf + i)) =
			*((u32 *) (ring->bounce_buf + copy + i));
	}

	for (i = copy - 4; i >= 4 ; i -= 4) {
		if ((i & (TXBB_SIZE - 1)) == 0)
			wmb();

		*((u32 *) (ring->buf + index * TXBB_SIZE + i)) =
			*((u32 *) (ring->bounce_buf + i));
	}

	/* Return real descriptor location */
	return ring->buf + index * TXBB_SIZE;
}

static void *get_frag_ptr(struct sk_buff *skb)
{
	struct skb_frag_struct *frag =  &skb_shinfo(skb)->frags[0];
	struct page *page = frag->page;
	void *ptr;

	ptr = page_address(page);
	if (unlikely(!ptr))
		return NULL;

	return ptr + frag->page_offset;
}

static int is_inline(struct sk_buff *skb, void **pfrag)
{
	void *ptr;

	if (inline_thold && !skb_is_gso(skb) && skb->len <= inline_thold) {
		if (skb_shinfo(skb)->nr_frags == 1) {
			ptr = get_frag_ptr(skb);
			if (unlikely(!ptr))
				return 0;

			if (pfrag)
				*pfrag = ptr;

			return 1;
		} else if (unlikely(skb_shinfo(skb)->nr_frags))
			return 0;
		else
			return 1;
	}

	return 0;
}

static int inline_size(struct sk_buff *skb)
{
	if (skb->len + CTRL_SIZE + sizeof(struct mlx4_wqe_inline_seg)
	    <= MLX4_INLINE_ALIGN)
		return ALIGN(skb->len + CTRL_SIZE +
			     sizeof(struct mlx4_wqe_inline_seg), 16);
	else
		return ALIGN(skb->len + CTRL_SIZE + 2 *
			     sizeof(struct mlx4_wqe_inline_seg), 16);
}

static int get_real_size(struct sk_buff *skb, struct net_device *dev,
			 int *lso_header_size)
{
	struct mlx4_en_priv *priv = netdev_priv(dev);
	int real_size;

	if (skb_is_gso(skb)) {
		*lso_header_size = skb_transport_offset(skb) + tcp_hdrlen(skb);
		real_size = CTRL_SIZE + skb_shinfo(skb)->nr_frags * DS_SIZE +
			ALIGN(*lso_header_size + 4, DS_SIZE);
		if (unlikely(*lso_header_size != skb_headlen(skb))) {
			/* We add a segment for the skb linear buffer only if
			 * it contains data */
			if (*lso_header_size < skb_headlen(skb))
				real_size += DS_SIZE;
			else {
				if (netif_msg_tx_err(priv))
					en_warn(priv, "Non-linear headers\n");
				return 0;
			}
		}
	} else {
		*lso_header_size = 0;
		if (!is_inline(skb, NULL))
			real_size = CTRL_SIZE + (skb_shinfo(skb)->nr_frags + 1) * DS_SIZE;
		else
			real_size = inline_size(skb);
	}

	return real_size;
}

static void build_inline_wqe(struct mlx4_en_tx_desc *tx_desc, struct sk_buff *skb,
			     void *fragptr)
{
	struct mlx4_wqe_inline_seg *inl = &tx_desc->inl;
	static int spc = MLX4_INLINE_ALIGN - CTRL_SIZE - sizeof *inl;

	if (skb->len <= spc) {
		inl->byte_count = cpu_to_be32(1 << 31 | skb->len);
		skb_copy_from_linear_data(skb, inl + 1, skb_headlen(skb));
		if (skb_shinfo(skb)->nr_frags)
			memcpy(((void *)(inl + 1)) + skb_headlen(skb), fragptr,
			       skb_shinfo(skb)->frags[0].size);

	} else {
		inl->byte_count = cpu_to_be32(1 << 31 | spc);
		if (skb_headlen(skb) <= spc) {
			skb_copy_from_linear_data(skb, inl + 1, skb_headlen(skb));
			if (skb_headlen(skb) < spc) {
				memcpy(((void *)(inl + 1)) + skb_headlen(skb),
					fragptr, spc - skb_headlen(skb));
				fragptr +=  spc - skb_headlen(skb);
			}
			inl = (void *) (inl + 1) + spc;
			memcpy(((void *)(inl + 1)), fragptr, skb->len - spc);
		} else {
			skb_copy_from_linear_data(skb, inl + 1, spc);
			inl = (void *) (inl + 1) + spc;
			skb_copy_from_linear_data_offset(skb, spc, inl + 1,
					skb_headlen(skb) - spc);
			if (skb_shinfo(skb)->nr_frags)
				memcpy(((void *)(inl + 1)) + skb_headlen(skb) - spc,
					fragptr, skb_shinfo(skb)->frags[0].size);
		}

		wmb();
		inl->byte_count = cpu_to_be32(1 << 31 | (skb->len - spc));
	}
}

u16 mlx4_en_select_queue(struct net_device *dev, struct sk_buff *skb)
{
	struct mlx4_en_priv *priv = netdev_priv(dev);
	u16 vlan_tag = 0;
	int tx_ind = 0;
	struct tcphdr *th = tcp_hdr(skb);
	struct iphdr *iph = ip_hdr(skb);
	struct mlx4_en_tx_hash_entry *entry;
	u32 hash_index;

	/* Obtain VLAN information if present */
	if (priv->vlgrp && vlan_tx_tag_present(skb)) {
		vlan_tag = vlan_tx_tag_get(skb);
		/* Set the Tx ring to use according to vlan priority */
		tx_ind = priv->tx_prio_map[vlan_tag >> 13];
		if (tx_ind)
			return tx_ind;
	}

	/* Hashing is only done for TCP/IP or UDP/IP packets */
	if (be16_to_cpu(skb->protocol) != ETH_P_IP)
		return MLX4_EN_NUM_HASH_RINGS;

	hash_index = be32_to_cpu(iph->daddr) & MLX4_EN_TX_HASH_MASK;
	switch(iph->protocol) {
	case IPPROTO_UDP:
		break;
	case IPPROTO_TCP:
		if (th) {
			hash_index = (hash_index ^ be16_to_cpu(th->dest ^ th->source)) &
					MLX4_EN_TX_HASH_MASK;
		}
		break;
	default:
		return MLX4_EN_NUM_HASH_RINGS;
	}

	entry = &priv->tx_hash[hash_index];
	if(unlikely(!entry->cnt)) {
		tx_ind = hash_index & (MLX4_EN_NUM_HASH_RINGS / 2 - 1);
		if (2 * entry->small_pkts > entry->big_pkts)
			tx_ind += MLX4_EN_NUM_HASH_RINGS / 2;
		entry->small_pkts = entry->big_pkts = 0;
		entry->ring = tx_ind;
	}

	entry->cnt++;
	if (skb->len > MLX4_EN_SMALL_PKT_SIZE)
		entry->big_pkts++;
	else
		entry->small_pkts++;
	return entry->ring;
}

static inline void mlx4_bf_copy(unsigned long *dst, unsigned long *src,
				unsigned bytecnt)
{
	__iowrite64_copy(dst, src, bytecnt / 8);
}

int mlx4_en_xmit(struct sk_buff *skb, struct net_device *dev)
{
	struct mlx4_en_priv *priv = netdev_priv(dev);
	struct mlx4_en_dev *mdev		= priv->mdev;
	struct mlx4_en_port_stats *port_stats	= &priv->port_stats;
	struct device *ddev			= priv->ddev;
	struct mlx4_mr *mr			= &mdev->mr;
	struct mlx4_en_tx_ring *ring;
	struct mlx4_en_tx_desc *tx_desc;
	struct mlx4_wqe_data_seg *data;
	struct skb_frag_struct *frag;
	struct mlx4_en_tx_info *tx_info;
	struct ethhdr *ethh;
	struct mlx4_wqe_ctrl_seg *ctrl;
	u64 mac;
	u32 mac_l, mac_h;
	int tx_ind = 0;
	int nr_txbb;
	int desc_size;
	int real_size;
	dma_addr_t dma;
	u32 index, bf_index;
	__be32 op_own;
	u16 vlan_tag = 0;
	int i;
	int lso_header_size;
	void *fragptr;
	bool bounce = false;
	int inflight;

	if (unlikely(!priv->port_up))
		goto tx_drop;

	real_size = get_real_size(skb, dev, &lso_header_size);
	if (unlikely(!real_size))
		goto tx_drop;

	/* Allign descriptor to TXBB size */
	desc_size = ALIGN(real_size, TXBB_SIZE);
	nr_txbb = desc_size / TXBB_SIZE;
	if (unlikely(nr_txbb > MAX_DESC_TXBBS)) {
		if (netif_msg_tx_err(priv))
			en_warn(priv, "Oversized header or SG list\n");
		goto tx_drop;
	}

	tx_ind = skb->queue_mapping;
	ring = priv->tx_ring[tx_ind];
	if (priv->vlgrp && vlan_tx_tag_present(skb))
		vlan_tag = vlan_tx_tag_get(skb);

	/* Check available TXBBs And 2K spare for prefetch */
	inflight = atomic_read(&ring->inflight);
	if (unlikely(inflight > ring->full_size)) {
		/* every full Tx ring stops queue */
		netif_tx_stop_queue(netdev_get_tx_queue(dev, tx_ind));
		ring->queue_stopped++;

		/* Check again whether the queue was cleaned */
		inflight = atomic_read(&ring->inflight);
		if (inflight <= ring->full_size) {
			netif_tx_wake_queue(netdev_get_tx_queue(dev, tx_ind));
			ring->wake_queue++;
		} else
			return NETDEV_TX_BUSY;
	}

	/* Track current inflight packets for performance analysis */
	AVG_PERF_COUNTER(pstats->inflight_avg,
			 (u32) (ring->prod - ring->cons - 1));

	/* Packet is good - grab an index and transmit it */
	index = ring->prod & ring->size_mask;
	bf_index = ring->prod;

	/* See if we have enough space for whole descriptor TXBB for setting
	 * SW ownership on next descriptor; if not, use a bounce buffer. */
	if (likely(index + nr_txbb <= ring->size))
		tx_desc = ring->buf + index * TXBB_SIZE;
	else {
		tx_desc = (struct mlx4_en_tx_desc *) ring->bounce_buf;
		bounce = true;
	}
	ctrl = &tx_desc->ctrl;

	/* Save skb in tx_info ring */
	tx_info = &ring->tx_info[index];
	tx_info->skb = skb;
	tx_info->nr_txbb = nr_txbb;

	/* Prepare ctrl segement apart opcode+ownership, which depends on
	 * whether LSO is used */
	ctrl->vlan_tag = cpu_to_be16(vlan_tag);
	ctrl->ins_vlan = MLX4_WQE_CTRL_INS_VLAN *
		!!vlan_tx_tag_present(skb);
	ctrl->fence_size = (real_size / 16) & 0x3f;
	ctrl->srcrb_flags = cpu_to_be32(MLX4_WQE_CTRL_SOLICITED);

	/*
	 * Completion is requested only when crossing 16 BBs boundary 
	 * for vlan tagged packets completion must be immediate
         */
	if (!!((index ^ (index + nr_txbb)) & (~0xf)) || vlan_tag)
		ctrl->srcrb_flags |= cpu_to_be32(MLX4_WQE_CTRL_CQ_UPDATE);

	if (likely(skb->ip_summed == CHECKSUM_PARTIAL)) {
		ctrl->srcrb_flags |= cpu_to_be32(MLX4_WQE_CTRL_IP_CSUM
			    | MLX4_WQE_CTRL_TCP_UDP_CSUM);
		ring->tx_csum++;
	}

	if (unlikely(priv->validate_loopback)) {
		/* Copy dst mac address to wqe */
		skb_reset_mac_header(skb);
		ethh = eth_hdr(skb);
		if (ethh) {
			mac = mlx4_en_mac_to_u64(ethh->h_dest);
			mac_h = (u32) ((mac & 0xffff00000000ULL) >> 16);
			mac_l = (u32) (mac & 0xffffffff);
			ctrl->srcrb_flags |= cpu_to_be32(mac_h);
			ctrl->imm = cpu_to_be32(mac_l);
		}
	}

	/* Handle LSO (TSO) packets */
	if (lso_header_size) {
		/* Mark opcode as LSO */
		op_own = cpu_to_be32(MLX4_OPCODE_LSO | (1 << 6)) | ((ring->prod & ring->size) ?
				cpu_to_be32(MLX4_EN_BIT_DESC_OWN) : 0);

		/* Fill in the LSO prefix */
		tx_desc->lso.mss_hdr_size = cpu_to_be32(
			skb_shinfo(skb)->gso_size << 16 | lso_header_size);

		/* Copy headers;
		 * note that we already verified that it is linear */
		memcpy(tx_desc->lso.header, skb->data, lso_header_size);
		data = ((void *) &tx_desc->lso +
			ALIGN(lso_header_size + 4, DS_SIZE));

		port_stats->tso_packets++;
		i = ((skb->len - lso_header_size) / skb_shinfo(skb)->gso_size) +
			!!((skb->len - lso_header_size) % skb_shinfo(skb)->gso_size);
		ring->bytes += skb->len + (i - 1) * lso_header_size;
		ring->packets += i;
	} else {
		/* Normal (Non LSO) packet */
		op_own = cpu_to_be32(MLX4_OPCODE_SEND) | ((ring->prod & ring->size) ?
			 cpu_to_be32(MLX4_EN_BIT_DESC_OWN) : 0);
		data = &tx_desc->data;
		ring->bytes += max(skb->len, (unsigned int) ETH_ZLEN);
		ring->packets++;

	}
	AVG_PERF_COUNTER(pstats->tx_pktsz_avg, skb->len);


	/* valid only for none inline segments */
	tx_info->data_offset = (void *) data - (void *) tx_desc;

	tx_info->linear = (lso_header_size < skb_headlen(skb) && !is_inline(skb, NULL)) ? 1 : 0;
	data += skb_shinfo(skb)->nr_frags + tx_info->linear - 1;

	if (!is_inline(skb, &fragptr)) {
		/* Map fragments */
		for (i = skb_shinfo(skb)->nr_frags - 1; i >= 0; i--) {
			frag = &skb_shinfo(skb)->frags[i];
			dma = dma_map_page(ddev, frag->page, frag->page_offset,
					   frag->size, PCI_DMA_TODEVICE);
			if (unlikely(dma_mapping_error(ddev, dma)))
				goto err_dma;
			data->addr = cpu_to_be64(dma);
			data->lkey = cpu_to_be32(mr->key);
			wmb();
			data->byte_count = cpu_to_be32(frag->size);
			--data;
		}

		/* Map linear part */
		if (tx_info->linear) {
			dma = dma_map_single(ddev, skb->data + lso_header_size,
					     skb_headlen(skb) - lso_header_size, PCI_DMA_TODEVICE);
			if (unlikely(dma_mapping_error(ddev, dma)))
				goto err_dma;
			data->addr = cpu_to_be64(dma);
			data->lkey = cpu_to_be32(mr->key);
			wmb();
			data->byte_count = cpu_to_be32(skb_headlen(skb) - lso_header_size);
		}
		tx_info->inl = 0;
	} else {
		build_inline_wqe(tx_desc, skb, fragptr);
		tx_info->inl = 1;
	}

	ring->prod += nr_txbb;
	atomic_add(nr_txbb, &ring->inflight);

	/* If we used a bounce buffer then copy descriptor back into place */
	if (bounce)
		tx_desc = mlx4_en_bounce_to_desc(ring, index, desc_size);

	/* Run destructor before passing skb to HW */
	if (likely(!skb_shared(skb)))
		skb_orphan(skb);

	if (ring->bf_enabled && desc_size <= MAX_BF && !bounce && !vlan_tag) {
		*(__be32 *) (&tx_desc->ctrl.vlan_tag) |= cpu_to_be32(ring->doorbell_qpn);
		op_own |= htonl((bf_index & 0xffff) << 8);
		/* Ensure new descirptor hits memory
		* before setting ownership of this descriptor to HW */
		wmb();
		ctrl->owner_opcode = op_own;

		wmb();

		mlx4_bf_copy(ring->bf.reg + ring->bf.offset, (unsigned long *) ctrl,
		     desc_size);

		wmb();

		ring->bf.offset ^= ring->bf.buf_size;
	} else {
		/* Ensure new descirptor hits memory
		* before setting ownership of this descriptor to HW */
		wmb();
		tx_desc->ctrl.owner_opcode = op_own;
		wmb();
		iowrite32be(ring->doorbell_qpn, ring->bf.uar->map + MLX4_SEND_DOORBELL);
	}
	dev->trans_start = jiffies;

	return 0;

err_dma:
	while (i++ < skb_shinfo(skb)->nr_frags - 1) {
		++data;
		frag = &skb_shinfo(skb)->frags[i];
		dma_unmap_page(ddev, (dma_addr_t) be64_to_cpu(data[i].addr),
			       frag->size, PCI_DMA_TODEVICE);
	}
tx_drop:
	dev_kfree_skb_any(skb);
	priv->stats.tx_dropped++;
	return NETDEV_TX_OK;
}

