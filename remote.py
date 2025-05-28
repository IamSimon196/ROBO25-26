import paramiko
import pygame
import time

RPI_HOST = "192.168.200.146"  
USERNAME = "admin"
PASSWORD = "admin"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(RPI_HOST, username=USERNAME, password=PASSWORD)
sftp = client.open_sftp()  


pygame.init()
screen = pygame.display.set_mode((100, 100))

angle = 0

try:
    while True:
        pygame.event.pump()

        key = pygame.key.get_pressed()

        if key[pygame.K_w] and key[pygame.K_a]:
            right_speed = 1.0
            left_speed = 0.0
        elif key[pygame.K_w] and key[pygame.K_d]:
            right_speed = 0.0
            left_speed = 1.0
        elif key[pygame.K_s] and key[pygame.K_a]:
            right_speed = -1.0
            left_speed = 0.0
        elif key[pygame.K_s] and key[pygame.K_d]:
            right_speed = 0.0
            left_speed = -1.0

        elif key[pygame.K_s]:
            right_speed = -1.0
            left_speed = -1.0
        elif key[pygame.K_w]:
            right_speed = 1.0
            left_speed = 1.0
        elif key[pygame.K_a]:
            right_speed = 1.0
            left_speed = -1.0
        elif key[pygame.K_d]:
            right_speed = -1.0
            left_speed = 1.0
        else:
            right_speed = 0
            left_speed = 0

        if key[pygame.K_e]:
            angle += 5.0
        elif key[pygame.K_f]:
            angle -= 5.0
        angle = max(0, min(angle, 180))
        print(angle)

        with sftp.file("/home/admin/remote/values.txt", "w") as file:
            file.write(f"{right_speed:.2f} {left_speed:.2f} {angle:.2f}")

        time.sleep(0.001)


except KeyboardInterrupt:
    sftp.close()
    client.close()
    pygame.quit()
