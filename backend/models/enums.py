from enum import Enum


class VisaType(str, Enum):
    h1b = "h1b"
    l1 = "l1"
    o1 = "o1"
    eb5 = "eb5"
    f1 = "f1"
    b1b2 = "b1b2"
    green_card = "green_card"
    family = "family"


class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class InterviewType(str, Enum):
    consular = "consular"
    adjustment_of_status = "adjustment_of_status"
    asylum = "asylum"
    naturalization = "naturalization"


class USCISForm(str, Enum):
    N400 = "N-400"
    I130 = "I-130"
    I765 = "I-765"
    I485 = "I-485"
    I90 = "I-90"
    I751 = "I-751"
    I131 = "I-131"
    I129 = "I-129"
    I140 = "I-140"
    I589 = "I-589"
    I539 = "I-539"
    O1 = "O-1"
    H1B = "H-1B"
    L1 = "L-1"
    B1B2 = "B-1/B-2"
    F1 = "F-1"
    AR11 = "AR-11"
