from enum import Enum


class Degree(str, Enum):
    BACHELOR = "Bachelor"
    PHD = "PhD"
    ASSOCIATE = "Associate"
    MASTER = "Master"


class Role(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
