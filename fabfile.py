from fabric import task
from invoke import Responder
from _credentials import github_username, github_password

def _get_github_auth_responders():
    username_responder = Responder(
        pattern="Username for 'https://github.com':",
        response='{}\n'.format(github_username)
        )

    password_responder = Responder(
        pattern="Password for 'https://{}@github.com'".format(github_username),
        response='{}\n'.format(github_password)
        )

    return [username_responder, password_responder]

@task()
# c 参数是 Fabric 在连接服务器时创建的 ssh 客户端实例，使用这个实例可以在服务器上运行相关命令
def deploy(c):
    supervisor_conf_path = '~/etc/'
    supervisor_program_name = 'blogweb_django'
 
    project_root_path = '~/apps/blogweb_django/'
 
    # 先停止应用
    with c.cd(supervisor_conf_path):
        cmd = 'supervisorctl stop {}'.format(supervisor_program_name)
        c.run(cmd)
 
    # 进入项目根目录，从 Git 拉取最新代码
    with c.cd(project_root_path):
        cmd = 'git pull'
        responders = _get_github_auth_responders()
        c.run(cmd, watchers=responders)
 
    # 重新启动应用
    with c.cd(supervisor_conf_path):
        cmd = 'supervisorctl start {}'.format(supervisor_program_name)
        c.run(cmd)