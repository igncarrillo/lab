def redFilter(leido,intensity):
    for i in range(0, len(leido) - 2, 3):
        leido[i] = int(leido[i] * (intensity / 100))
        if leido[i] > 255:
            leido[i] = 255
        leido[i + 1] = 0
        leido[i + 2] = 0

    return bytes(leido)

def greenFilter(leido,intensity):
    for i in range(1, len(leido) - 1, 3):
        leido[i] = int(leido[i] * (intensity / 100))
        if leido[i] > 255:
            leido[i] = 255
        leido[i - 1] = 0
        leido[i + 1] = 0
    return bytes(leido)

def blueFilter(leido,intensity):
    for i in range(2, len(leido), 3):
        leido[i] = int(leido[i] * (intensity / 100))
        if leido[i] > 255:
            leido[i] = 255
        leido[i - 1] = 0
        leido[i - 2] = 0
    return bytes(leido)

def whiteFilter(leido,intensity):
    for i in range(0, len(leido) - 2, 3):
        prom = int((leido[i] + leido[i + 1] + leido[i + 2]) / 3)
        leido[i] = leido[i + 1] = leido[i + 2] = prom
        leido[i] = int(leido[i] * (intensity / 100))
        if leido[i] > 255:
            leido[i] = 255
        leido[i + 2] = leido[i + 1] = leido[i]
    return bytes(leido)

def noneFilter(leido,intensity):
    for i in range(0, len(leido), 1):
        leido[i] = int(leido[i] * (intensity / 100))
        if leido[i] > 255:
            leido[i] = 255
    return bytes(leido)