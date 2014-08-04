"""Deployment automation scripts"""
import os
import posixpath
from contextlib import contextmanager
from fabric.api import env, task, hide, local, puts, lcd, prefix, cd

PROJECT_NAME = 'alma.net'
BASE_DIR = '/home/anguix/work/projects/test/alma.net'


env.project_name = PROJECT_NAME
env.repository = 'git@github.com:Mafioso/{project_name}.git'.format(**env)
env.local_branch = 'develop'
env.remote_ref = 'origin/develop'
env.requirements_file = 'requirements.txt'
env.restart_command = 'supervisorctl restart {project_name}'.format(**env)
env.restart_sudo = False


@task
def dev():
    env.virtualenv_dir = os.path.abspath(
        os.path.join(BASE_DIR, 'alma.net'))
    env.activate_venv = '. {virtualenv_dir}/bin/activate'.format(**env)
    env.project_dir = '{virtualenv_dir}/{project_name}'.format(**env)


# set default env
dev()


@task
def bootstrap(action=''):
    with hide('running', 'stdout'):
        exists = local('if [ -d "{virtualenv_dir}" ]; then echo 1; fi'.format(
                       **env), capture=True)
    if exists and not action == 'force':
        puts('Assuming has already been bootstrapped since '
             '{virtualenv_dir} exists.'.format(**env))
        return
    if not exists:
        local('mkdir -p {0}'.format(posixpath.dirname(env.virtualenv_dir)))
        local('virtualenv {virtualenv_dir} --no-site-packages'.format(**env))
        with lcd(env.virtualenv_dir):
            local('mkdir media static {project_name}'.format(**env))
            lcd(env.project_name)
            local('git clone {repository} {project_dir}'.format(**env))

    with local_venv():
        with lcd(env.project_dir):
            local('pip install -r {requirements_file}'.format(**env))
            local('touch project.pth')
            local('echo "{project_dir}/src" > project.pth'.format(**env))
            local('ln -sf {project_dir}/project.pth {virtualenv_dir}/lib/'
                  'python2.7/site-packages/{project_name}.pth'.format(**env))
    puts('Project bootstraping finished succesfully.')


@contextmanager
def local_venv():
    with prefix(env.activate_venv):
        yield


@contextmanager
def venv():
    with prefix(env.activate_venv):
        yield
