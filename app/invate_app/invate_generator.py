import cv2
import qrcode


def generate_qrcode(parent_id):
    dns_name = 'https://vk.com/id'
    filename = parent_id + '.png'
    img = qrcode.make(dns_name+parent_id)
    return img.save(filename)


generate_qrcode('1')