import commands
from docker import Client
class Image:

    def __init__(self, image='zlpl/ubuntu-test:latest'):
        self.cli = Client(base_url='unix://var/run/docker.sock')
        self.id = self.cli.create_container(image=image, command='bash', tty=True)['Id']
        self.cli.start(self.id)

    def __del__(self):
        self.cli.stop(self.id)
        self.cli.remove_container(self.id)

    #url must come from 'files'
    def copy(self, url):
        #dir_url='/'.join(url.split("/")[0:-1])
        dir_url=url[0:url.rfind('/')]
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' mkdir -p '+dir_url)
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' cp -af changed_files'+url+' '+url)
        return status, output

    #url must come from 'directories'
    def mkdir(self, url):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' mkdir -p '+url)

    #url can be from either 'files' or 'directories'
    def copy_from_conf(self, url):
        dir_url=url[0:url.rfind('/')]
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' mkdir -p '+dir_url)
        (status, output) = commands.getstatusoutput('docker cp changed_files/nginx.conf '+self.id+':'+url)

    def copy_from_html(self, url):
        dir_url=url[0:url.rfind('/')]
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' mkdir -p '+dir_url)
        (status, output) = commands.getstatusoutput('docker cp changed_files/index.html '+self.id+':'+url)

    #name must come from 'packages'
    def install_package(self, name):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' apt-get install --fix-missing -y '+name)
        #return status, output

    def remove_package(self, name):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' apt-get remove -y '+name)

    def remove_package_force(self, name):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' dpkg --remove --force-depends '+name)

    def restart_nginx(self):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' service nginx restart')

    def start_nginx(self):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' service nginx start')

    def stop_nginx(self):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' service nginx stop')

    def kill_nginx(self):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' kill `ps -ef|grep "nginx: master"|grep -v grep`')

    #It should return True if everything is right.
    def get_html(self):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' curl localhost:8011')
        return 'Running nginx' in output

    #existent files will end with its modified time, but non-exsistent files will only have file names outputed. 
    #The output is like:
    #/var/log/nginx/access.log 2016-07-16 12:34:08.692963831
    #/var/log/nginx/error.log
    def ll_all(self):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' bash ls.sh')
        return output

    #The raw output of 'ls -ld' like:
    #drwxr-xr-x 87 root root 4096 Jul 16 12:15 /etc
    def ll(self, url):
        (status, output) = commands.getstatusoutput('docker exec '+self.id+' ls -ld '+url)
        return output
    

def create_clean_image():
    return Image()

def create_wrong_image():
    return Image('zlpl/ubuntu-nginx-remove-libxml2')
'''
An successful running example:
'''

#i = create_clean_image()
i = create_wrong_image()

try:
    i.install_package('nginx')
    i.copy_from_conf('/etc/nginx')
    i.copy_from_html('/var')
    i.restart_nginx()
    print i.get_html()
finally:
    del i
