import docker
import sys
import json
import logging
import datetime
import time
import requests
import subprocess

if __name__ == "__main__":
    client = docker.from_env()

    count = 0
    with open('parameters.json') as json_data:
        stream = json.load(json_data)

    logging.basicConfig(level=logging.INFO)
    logging.info("{time}: [Server] Initiating creation of docker container".format(time=datetime.datetime.now()))

    container = client.containers.run(
        image=stream.get('image'),
        auto_remove=True,
        detach=True,
        environment=stream.get('env_vars'),
        ports=stream.get('initial_deployment').get('ports'),
        volumes=stream.get('volumes')
        )
    container_id = container.id
    container_name = container.name

    logging.info("{time}: [Server] Container launched successfully. \nID: {id}\nName: {name}".format(
        time=datetime.datetime.now(),
        id=container.id,
        name=container.name
    ))
    
    try:
      path = stream.get('healthCheck').get('path')
    except:
      print ("Path not provided, continuing with /")
      path = "/"

    logging.info("{time}: [Server] Initiating healthcheck for http://localhost:{port}/{path}".format(
        time=datetime.datetime.now(),
        port=stream.get('healthCheck').get('port'),
        path=path
    ))
    method = stream.get('healthCheck').get('method')
    time.sleep(5)
    while count != 3:
        api = "http://localhost:{}/{}".format(stream.get('healthCheck').get('port').strip(),path)
        status = requests.get(api).status_code
        if status == 200:
            count += 1
        else:
            subprocess.Popen('docker stop %s' %container_id, shell=True).communicate()
#            client.containers.stop(container_id)
            logging.info("{time}: [Server] HealthCheck for http://localhost:{port}/{path} failed".format(
                time=datetime.datetime.now(),
                port=stream.get('healthCheck').get('port'),
                path=path
            ))
            exit(1)
        time.sleep(10)

    logging.info("{time}: [Server] HealthCheck for http://localhost:{port}/{path} successful".format(
        time=datetime.datetime.now(),
        port=stream.get('healthCheck').get('port'),
        path=path
    ))
#    client.containers.stop(container.id)
    subprocess.Popen('docker stop %s' %container_id, shell=True).communicate()
    for container in client.containers.list():
        if container.name == str(stream.get('container')):
#            client.containers.stop(container.id)
            subprocess.Popen('docker stop %s' %stream.get('container'), shell=True).communicate()
            subprocess.Popen('docker rm %s' %stream.get('container'), shell=True).communicate()
            container = client.containers.run(
                image=stream.get('image'),
                auto_remove=True,
                detach=True,
                name=str(stream.get('container')),
                environment=stream.get('env_vars'),
                ports=stream.get('ports'),
                volumes=stream.get('volumes')
                )
            logging.info("{time}: [Server] Container launched successfully. \nID: {id}\nName: {name}".format(
                time=datetime.datetime.now(),
                id=container.id,
                name=container.name
            ))
