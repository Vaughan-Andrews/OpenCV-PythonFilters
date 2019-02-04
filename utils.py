# -*- coding: utf-8 -*-

def img_paste(src, target, left, top):
   
    height, width, _  = src.shape
    maxH, maxW, _ = target.shape
    startH = 0 if top >= 0 else abs(top)
    endH = height if top + height < maxH else maxH - top
    startW = 0 if left >= 0 else abs(left)
    endW = width if left + width < maxW else maxW - left
    for i in range(startH, endH):
        for j in range(startW, endW):
            if src.item(i, j, 3) > 150:
                target.itemset((top + i, left + j, 0), src.item(i, j, 0))
                target.itemset((top + i, left + j, 1), src.item(i, j, 1))
                target.itemset((top + i, left + j, 2), src.item(i, j, 2))
