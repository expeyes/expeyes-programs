import expeyes.eyes17, time
from expeyes.SENSORS import MPU6050

p=expeyes.eyes17.open()

S = MPU6050.connect(p.I2C)

print S.getRaw() #[Ax,Ay,Az,Temperature,Gx,Gy,Gz]
print S.getAccel() #[Ax,Ay,Az]
print S.getGyro() #[Gx,Gy,Gz]
