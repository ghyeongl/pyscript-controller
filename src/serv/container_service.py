import subprocess

class ContainerService:
    def list_containers(self):
        """
        docker ps -a 명령을 실행하여 컨테이너 목록(이름)을 반환
        --format "{{.Names}}" 옵션을 주어, 컨테이너 이름만 리스트로 받는다.
        """
        output = subprocess.check_output(["docker", "ps", "-a", "--format", "{{.Names}}"])
        lines = output.decode("utf-8").strip().splitlines()
        return lines

    def start_container(self, cont_name):
        """
        docker start <container_name> 실행
        """
        containers = self.list_containers()
        if cont_name not in containers:
            raise ValueError(f"Container '{cont_name}' does not exist. (from docker ps -a)")
        
        subprocess.run(["docker", "start", cont_name], check=True)

    def stop_container(self, cont_name):
        """
        docker stop <container_name> 실행
        """
        containers = self.list_containers()
        if cont_name not in containers:
            raise ValueError(f"Container '{cont_name}' does not exist. (from docker ps -a)")

        subprocess.run(["docker", "stop", cont_name], check=True)
