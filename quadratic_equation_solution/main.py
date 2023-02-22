a, b, c = map(float, input('Введите коэффициенты квадратного уравнения a, b, c:').split())
dis = b ** 2 - 4 * a * c

if dis > 0:
    x1 = (-b + dis**(1/2)) / (2 * a)
    x2 = (-b - dis**(1/2)) / (2 * a)
    print('x1 =', x1)
    print('x2 =', x2)
elif dis == 0:
    x = -b / (2 * a)
    print('x =', x)
else:
    print('Корней нет!')
