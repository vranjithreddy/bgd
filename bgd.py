import docker
import sys
import json
import logging
import datetime
import time
import requests

if __name__ == "__main__":
    client = docker.from_env()

    count = 0
    with open('parameters.json', 'r') as json_data:
        stream = json.load(json_data)

    logging.basicConfig(level=logging.INFO)
    logging.info("{time}: [Server] Initiating creation of docker container".format(time=datetime.datetime.now()))

    container = client.containers.run(
        image=stream.get('image'),
        auto_remove=1,
        detach=true,
        environment=stream.get('env_vars'),
        ports=stream.get('ports'),
        volumes=stream.get('volumes')
        )

    logging.info("{time}: [Server] Container launched successfully. \nID: {id}\nName: {name}".format(
        time=datetime.datetime.now(),
        id=container.id,
        name=container.name
    ))

    logging.info("{time}: [Server] Initiating healthcheck for http://localhost:{port}/{path}".format(
        time=datetime.datetime.now(),
        port=stream.get('healthCheck').get('port'),
        path=stream.get('healthCheck').get('path')
    ))
    method = stream.get('healthCheck').get('method')
    while count != 10:
        status = requests.get('http://localhost:{port}/{path}'.format(
            port = stream.get('healthCheck').get('port'),
            path = stream.get('healthCheck').get('path')
        )).status_code
        if status == 200:
            count += 1
        else:
            client.container.stop(container.id)
            logging.info("{time}: [Server] HealthCheck for http://localhost:{port}/{path} failed".format(
                time=datetime.datetime.now(),
                port=stream.get('healthCheck').get('port'),
                path=stream.get('healthCheck').get('path')
            ))
            exit(1)
        time.sleep(10)

    logging.info("{time}: [Server] HealthCheck for http://localhost:{port}/{path} successful".format(
        time=datetime.datetime.now(),
        port=stream.get('healthCheck').get('port'),
        path=stream.get('healthCheck').get('path')
    ))
    client.container.stop(container.id)
    for container in client.containers.list():
        if container.name == str(stream.get('container')):
            client.container.stop(container.id)
            container = client.containers.run(
                image=stream.get('image'),
                auto_remove=true,
                detach=true,
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
