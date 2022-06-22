import math

from numpy import False_
from DrivingInterface.drive_controller import DrivingController


before = 0
class DrivingClient(DrivingController):
    def __init__(self):
        # =========================================================== #
        #  Area for member variables =============================== #
        # =========================================================== #
        # Editing area starts from here
        #

        self.is_debug = False

        # api or keyboard
        self.enable_api_control = True # True(Controlled by code) /False(Controlled by keyboard)
        super().set_enable_api_control(self.enable_api_control)

        self.track_type = 99

        self.is_accident = False
        self.recovery_count = 0
        self.accident_count = 0

        #
        # Editing area ends
        # ==========================================================#
        super().__init__()
    
    def control_driving(self, car_controls, sensing_info):

        # =========================================================== #
        # Area for writing code about driving rule ================= #
        # =========================================================== #
        # Editing area starts from here
        #

        if self.is_debug:
            print("=========================================================")
            print("[MyCar] to middle: {}".format(sensing_info.to_middle))

            print("[MyCar] collided: {}".format(sensing_info.collided))
            print("[MyCar] car speed: {} km/h".format(sensing_info.speed))

            print("[MyCar] is moving forward: {}".format(sensing_info.moving_forward))
            print("[MyCar] moving angle: {}".format(sensing_info.moving_angle))
            print("[MyCar] lap_progress: {}".format(sensing_info.lap_progress))

            print("[MyCar] track_forward_angles: {}".format(sensing_info.track_forward_angles))
            print("[MyCar] track_forward_obstacles: {}".format(sensing_info.track_forward_obstacles))
            print("[MyCar] opponent_cars_info: {}".format(sensing_info.opponent_cars_info))
            print("[MyCar] distance_to_way_points: {}".format(sensing_info.distance_to_way_points))
            print("=========================================================")

        # half_load_width = self.half_road_limit - 1.25
        car_controls.throttle = 1
        car_controls.brake = 0


        # way points 좌표 시작
        middle = sensing_info.to_middle
        spd = sensing_info.speed


        if middle >= 0:
            points = [middle,] + sensing_info.distance_to_way_points
            angles = [0,] + sensing_info.track_forward_angles
            bo = [90, ]
            ts = []
            for i in range(20):
                C = 180 - bo[i] - (angles[i+1] - angles[i])
                temp = points[i] * math.sin(C * math.pi / 180) / points[i+1]
                A =  math.asin(temp if abs(temp) <= 1 else int(temp)) * 180 / math.pi
                bo.append(A)
                target = 180 - C - A
                ts.append(target)

            # way point 각도
            ways = []
            for j in range(20): 
                ways.append([points[j+1] * math.sin(sum(ts[:j+1]) * math.pi / 180), - points[j+1] * math.cos(sum(ts[:j+1]) * math.pi / 180)])

        else:
            points = [-middle,] + sensing_info.distance_to_way_points
            angles = [0, ] + [-angle for angle in sensing_info.track_forward_angles]
            bo = [90, ]
            ts = []
            for i in range(20):
                C = 180 - bo[i] - (angles[i+1] - angles[i])
                temp = points[i] * math.sin(C * math.pi / 180) / points[i+1]
                A =  math.asin(temp if abs(temp) <= 1 else int(temp)) * 180 / math.pi
                bo.append(A)
                target = 180 - C - A
                ts.append(target)

            ways = []
            for j in range(20):
                ways.append([points[j+1] * math.sin(sum(ts[:j+1]) * math.pi / 180), points[j+1] * math.cos(sum(ts[:j+1]) * math.pi / 180)])
            

        # 조절해서 쓰기
        if spd < 110:
            tg = 4
        elif spd < 130:
            tg = 5
        elif spd < 150:
            tg = 6
        else:
            tg = 7




        target = ways[tg][:]

        # 아래 부분에 원하는 좌표 넣기

        # target = 

        theta = math.atan(target[1] / target[0]) * 180 / math.pi - sensing_info.moving_angle

        # theta 값의 범위 적당히 조정
        # 마찬가지로 steering도 상수값 조정하면 됨

        # 끝
        # 좌표는 ways에 순서대로

        obs = []
        near = points[0] * math.cos((90 - angles[1]) * math.pi / 180) + points[1] * math.cos(bo[1] * math.pi / 180)
        for obj in sensing_info.track_forward_obstacles:
            d, m = obj['dist'] - near, obj['to_middle']
            if d <= 0:
                n, k = -1, obj['dist']
                ang = (90 - angles[n+1]) * math.pi / 180
                obs.append([k * math.sin(ang) - m * math.cos(ang), -middle + k * math.cos(ang) + m * math.sin(ang)])
    
            else:
                n, k = int(d // 10), d % 10
                if n+2 > 10:
                    break
                ang = (90 - angles[n+1]) * math.pi / 180
                obs.append([ways[n][0] + k * math.sin(ang) - m * math.cos(ang), ways[n][1] + k * math.cos(ang) + m * math.sin(ang)])


        # 아웃 인 아웃 구현
        if angles[1] < 5 and angles[tg] < 5:
            print(1)
            car_controls.steering = 0
            if angles[-1] > 90 and middle > -5:
                theta = math.atan(target[1] / (target[0]+4)) * 180 / math.pi - sensing_info.moving_angle
            elif angles[-1] < -90 and middle < 5:
                theta = math.atan(target[1] / (target[0]-4)) * 180 / math.pi - sensing_info.moving_angle

        if spd < 110:
            car_controls.steering = theta / 120
        else:
            car_controls.steering = theta / 100


        if abs(angles[-1]) > 120 and spd > 130:
            car_controls.throttle = 0
            car_controls.brake = 0.5
            if abs(theta) > 40:
                car_controls.steering = 1 if theta >= 0 else -1


        
        if self.is_debug:
            print("[MyCar] steering:{}, throttle:{}, brake:{}".format(car_controls.steering, car_controls.throttle, car_controls.brake))

        #
        # Editing area ends
        # ==========================================================#
        return car_controls


    # ============================
    # If you have NOT changed the <settings.json> file
    # ===> player_name = ""
    #
    # If you changed the <settings.json> file
    # ===> player_name = "My car name" (specified in the json file)  ex) Car1
    # ============================
    def set_player_name(self):
        player_name = ""
        return player_name


if __name__ == '__main__':
    print("[MyCar] Start Bot! (PYTHON)")
    client = DrivingClient()
    return_code = client.run()
    print("[MyCar] End Bot! (PYTHON)")

    exit(return_code)
