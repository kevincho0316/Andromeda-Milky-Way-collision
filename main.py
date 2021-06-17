'''
run on python 3.6 and
계산은 풀 스케일로 계산하고 출력은 작은 버전으로 
'''


from __future__ import division

from vpython import vector, color, sqrt, sphere, rate, scene,keysdown,vec,label
from math import fsum,floor
from random import gauss, randint
import numpy as np


scene.width = 1300
scene.height = 650






# 상수
# 만유 중력 상수
G = 6.673e-11

# 평균 별들의 질량
SolarMass = 1.989e30

# 별들의 질량 범위 만들기
MIN_SolarMass = SolarMass * 0.5
MAX_SolarMass = SolarMass * 256
AVG_SolarMass = SolarMass * 0.3

# 스케일
kScale = 3e16# 3e16  

# 범위 설정
MAX_Orbit_RADIUS = kScale * 10
MIN_Orbit_RADIUS = kScale * 0.15


# 두께 설정
MILKY_WAY_GALAXY_THICKNESS = kScale * 0.4
ANDROMEDA_GALAXY_THICKNESS = kScale  * 0.67


# 우리 은하는 3,000억개의 별 개수를 가지고 있다.
# 안드로메다는 1 조개의 별을 가짐
# 약 3.3배 차이 
NumOfStar_MIlky = 500
NumOfStar_Andromeda = floor(NumOfStar_MIlky * 3.33333)

# 그래픽 
STAR_RADIUS = 0.025
distance = 7e11     #그래픽과 실제 물리 계산을 할때와 실제 렌더링을 할때의 크기 차이 


# 함수_______________________________________________________

#인터 페이스
def Ui(pos_s, vel, mass):
    label( pos=pos_s, text='The <b>mass <i>M</i></b> = '+ str(mass) )
    


# x를 제한
def Limiter(x, low, high):
    return max(min(x,high), low)


#가속도 계산 함수
def gravity_acceleration(mass, radius):
    # 너무 많은 입자들이 튕겨 나가지 말라고 만든 장치
    radius = max(radius, MIN_Orbit_RADIUS)
    return G * mass / radius**2     #f = G m1 m2 / r² 에서 m을 이항 해 f/m1 = G  m2 / r² | f=ma라는 공식에 맞추어 가속도를 구함


def acceleration(obj, galaxy):
    r_galaxy = galaxy.pos - obj.pos
    return r_galaxy.norm() * gravity_acceleration(galaxy.mass, r_galaxy.mag)                     #별표ㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛㅛ


# 작용하는 중력의 힘
def gravity(mass1, mass2, radius):
    return G * mass1 * mass2 / radius**2  #만유인력 법칙 F = G m1 m2 / r²

# Calculate acceleration on an object caused by galaxy

def selector(galaxy_star,i):
    selected = i
    while selected == i: 
        selected = randint(0,galaxy_star-1)
    return selected




# 갤럭시의 클래스를 만들어준다. (두개를 만들어야 하기 때문에)
class Galaxy(object):
    def __init__(self, num_stars, pos, vel, radius, thickness, color): #변수 입력 받음
        self.pos = pos
        self.vel = vel
        self.radius = radius

        # 가우스 분포로 별 질량을 별 개수만큼 생성 생성
        masses = [Limiter(gauss(mu=AVG_SolarMass, sigma=AVG_SolarMass / 3.0), MIN_SolarMass, MAX_SolarMass)
                  for i in range(num_stars)]    #뒤에 반복문 달아도 반복이 됨 코드 양을 줄임

        # 은하의 질량이 전체 별의 질량이기에 이를 전체 더해준다.
        self.mass = fsum(masses)

        # 가우스 분포의 위치 시그마 xyz
        S_x = radius * 0.1
        S_y = thickness * 0.10
        S_z = radius * 0.1

        positions = []
        for i in range(num_stars):
            pos = vector(
                Limiter(gauss(mu=0, sigma=S_x), -radius, radius),
                Limiter(gauss(mu=0, sigma=S_y), -thickness, thickness),
                Limiter(gauss(mu=0, sigma=S_z), -radius, radius)
            )

            # 입자가 무지성으로 날아다니는걸 막음
            if pos.mag < MIN_Orbit_RADIUS:
                pos.mag = MIN_Orbit_RADIUS

            positions.append(pos)

        def orbital_Vel(center_mass, radius):                #공전속도 계산
            return sqrt(G * center_mass / radius)           #F=m* v²/r (구심력 공식) = F = G m1 m2 / r²  바탕화면 사진

        # 별 리스트 생성
        stars = []
        
        up = vector(0.0, 1.0, 0.0)  #위를 향하는 벡터 속도를 구할때 써야함

        for i in range(num_stars):
            # 정규화된 벡터를 이동방향에 따라 계산함                                                     
            a_pos = positions[i] + self.pos      #실제 좌표에서의 별의 위치
            r_pos = positions[i]                 #은하 내에서의 상대적 별의 위치
            
            vec = r_pos.cross(up).norm()         #위를 향하는 벡터와 은하으로 부터의 위치를 곱한다.이거는 공이 움직이는 방향만을 나타낸다.   
            
            r_vel = vec * orbital_Vel(self.mass, r_pos.mag) # 위에서 공의 방향을 구했으니 이를 속도와 곱해서 벡터(힘과 방향을 복합적으로 나타냄)를 구한다. 
            a_vel = r_vel + vel           #실제 속도를 구한다. 상대적인 속도와 은하의 속도를 더함으로써

            stars.append(Star(                          #구를 만들어달라고 신청을 한다.
                mass=masses[i],
                radius=STAR_RADIUS,
                pos=a_pos,
                vel=a_vel,
                color=color,
                
            ))

        self.stars = np.array(stars)




# 별의 클래스를 만들어준다. (어ㅓㅓㅓㅓㅁ청 마니 만들어야 하기에)
class Star(object):
    def __init__(self, mass, radius, pos, vel, color):
        self.obj = sphere(pos=pos / kScale, radius=radius, color=color, make_trail = True, retain=3)     #구 만들기
        self.mass = mass
        self.vel = vel
        self._pos = pos

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self.obj.pos = value / kScale
        self._pos = value

    def __str__(self):
        return "Mass: " + str(self.mass) + "\nPos: " + str(self.pos) + \
            "\nVel: " + str(self.vel)



def main():
    t = 0
    milky_way = Galaxy(
        num_stars=NumOfStar_MIlky,
        pos=vector(-3, 0, 0) * kScale,
        vel=vector(0, 0, 0),
        radius=MAX_Orbit_RADIUS,
        thickness=MILKY_WAY_GALAXY_THICKNESS,
        color=vector(1, 0, 0)
    )
    andromeda = Galaxy(
        num_stars=NumOfStar_Andromeda,
        pos=vector(3, 0, 0) * kScale,
        vel=vector(0, 3, 0),
        radius=MAX_Orbit_RADIUS,
        thickness=ANDROMEDA_GALAXY_THICKNESS,
        color=vector(0, 0, 1)
    )

# //////////////////////////////////////////////////////////////////////////
    tracker = sphere(pos=vector(10,0,0), radius = 0.05, make_trail = True, retain=10)
    v = vector(0,0,0)
    dv = 0.1
    dt = 0.01
    # amda = sphere(make_trail = True)
    
    scene.camera.follow(tracker)
    targeted_star = 1
    track_galaxy_num = NumOfStar_MIlky
    track_galaxy = milky_way
    track_mode = False

    L = label( xoffset=20,yoffset=50,height=13)
    
    while True:
        rate(100)

        mag_difference = milky_way.pos.mag - andromeda.pos.mag  #크기 차이

        for i in range(len(milky_way.stars)):
            star = milky_way.stars[i]
            star.vel += acceleration(star, andromeda) * distance + acceleration(star, milky_way) * distance
            star.pos += star.vel * distance
            if i == 35:
                star
        
            

        andromeda_mask = np.zeros(len(andromeda.stars))

        for star in andromeda.stars:
            star.vel += acceleration(star, milky_way) * distance + acceleration(star, andromeda) * distance
            star.pos += star.vel * distance

          

        milky_way.vel += acceleration(milky_way, andromeda) * distance
        milky_way.pos += milky_way.vel * distance

        andromeda.vel += acceleration(andromeda, milky_way) * distance
        andromeda.pos += andromeda.vel * distance
        

        t += distance

        # tracker
        k = keysdown()
        if 'e' in k: 
            if track_galaxy == milky_way:
                track_galaxy_num = NumOfStar_Andromeda
                track_galaxy = andromeda
        elif 'q' in k:
            if track_galaxy == andromeda:
                track_galaxy_num = NumOfStar_MIlky
                track_galaxy = milky_way

        elif 'f' in k:
            targeted_star = selector(track_galaxy_num-1,targeted_star)
        elif 'alt' in k:
            track_mode = True
            L.visible = False
            tracker.visible = False
        elif 't' in k:
            track_mode = False
            L.visible = True
            tracker.visible = True
        elif 'j' in k:
            if L.visible == False:
                L.visible = True
        elif 'h' in k:
            if L.visible == True:
                L.visible = False
        elif 'o' in k:
            while True:
                k = None
                k = keysdown()
                if 'p' in k:
                    break
                elif 'm' in k:
                    scene.capture(str(targeted_star)+'.png')    
                    k = None            # 여기ㅣㅣㅣㅣㅣㅣㅣㅣㅣㅣㅣㅣㅣㅣㅣ





        if track_mode == False:
            try:
                tracker.pos = track_galaxy.stars[targeted_star].pos /kScale
                L.pos = tracker.pos
                L.text = str(track_galaxy.stars[targeted_star])
                
            except :
                print("묵살")
        else:
            if 'a' in k: v.x -= dv
            if 'd' in k: v.x += dv
            if 's' in k: v.y -= dv
            if 'w' in k: v.y += dv
            if 'q' in k: v.z -= dv
            if 'e' in k: v.z += dv
            
            tracker.pos = v


if __name__ == '__main__':
    
    main()