import os, subprocess, time
remote = 'flag1'
tostart = ['BANKA']
user = os.getenv('USER')
env = "~/.bash_profile"
dir = "$DIBAS_DIR/versions/stableGUI/lib/python"
prgm = "CGRemote.py"
#cmd = "ssh -f %s@%s \"source %s; cd %s python %s %s\""
#print cmd % (user, remote, env, dir, prgm, ' '.join(tostart))
#val = os.system(cmd % (user, remote, env, dir, prgm, ' '.join(tostart)))

# cmd = "ssh -ft %s@%s"
# cmd2 = "source %s"
# cmd3 = "cd %s"
# cmd4 = "python %s %s"
# os.system(cmd % (user, remote))
# os.system(cmd2 % env)
# os.system(cmd3 % dir)
# os.system(cmd4 % (prgm, ' '.join(tostart)))

cmd = "ssh -f %s@%s source %s; cd %s; python %s %s"
cmd = cmd % (user, remote, env, dir, prgm, " ".join(tostart))
print cmd.split(" ")

subprocess.Popen(cmd.split(" "))

time.sleep(5)
prgm = "CGRemote"
sig = "SIGINT"
cmd = "ssh -q %s@%s"
#cmd = cmd % (user, remote, prgm, sig)
cmd = cmd % (user, remote)
print cmd
cmd = cmd.split(" ")
cmd.append("ps aux | grep -e %s | grep -v grep | awk '{print $2}' | xargs -r kill -%s" % (prgm, sig))
print cmd
subprocess.Popen(cmd)
#subprocess.Popen(["ssh", "-f", "mburnett@flag1", "source", "~/.bash_profile;", "cd", "$DIBAS_DIR/versions/stableGUI/lib/python;", "python", "CGRemote.py", "BANKA"])
# print" ".join(["ssh", "-f", "mburnett@flag1", "\"source", "~/.bash_profile;", "cd", "$DIBAS_DIR/versions/stableGUI/lib/python;", "python", "CGRemote.py", "BANKA\""])
