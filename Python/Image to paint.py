from PIL import Image
import numpy as np

if __name__ == '__main__':
    src = input()

    L = np.asarray(Image.open(src).convert('L')).astype('float')

    depth = 10
    grad = np.gradient(L)

    grad_x, grad_y = grad
    grad_x = grad_x * depth / 100
    grad_y = grad_y * depth / 100
    A = np.sqrt(grad_x ** 2 + grad_y ** 2 + 1)
    uni_x = grad_x / A
    uni_y = grad_y / A
    uni_z = 1 / A

    # 处理光源
    el = np.pi / 2.2
    az = np.pi / 4
    dx = np.cos(el) * np.cos(az)
    dy = np.cos(el) * np.sin(az)
    dz = np.sin(el)

    gd = 255 * (dx * uni_x + dy * uni_y + dz * uni_z)
    gd = gd.clip(0, 255)

    im = Image.fromarray(gd.astype('uint8'))
    im.save('./result.jpg')