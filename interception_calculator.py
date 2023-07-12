##################################################
# author: elovi                                  #
# time: 2021-04-16                               #
##################################################

'''
v1.2 changelog
1. 修正了风炮判定距离的错误
2. 拦截延迟以炮->炮为基准
3. 更新了巨人坐标计算相关的数据和机制（I3冰=11；初次冰冻399~599）
4. wave支持填写多个冰时机
5. 拦截行数在所有情况下都默认为2
'''

from inspect import cleandoc
import sys
from garg_pos import *
from help_text import *

rowHeight = 85
colWidth = 80
delayMustFallen = 450
isRoof = False

windPaoDist = [[125, 124, 84], [125, 125, 102], [125, 125, 114], [125, 125, 121], [124, 125, 124], [121, 125, 125], [118, 125, 125], [118, 125, 125]]

def scene(pscene, oppress=False):
    global rowHeight
    global isRoof
    if pscene == "PE" or pscene == "FE":
        rowHeight = 85
        isRoof = False
        if not oppress:
            print("已设置场地为六行")
    elif pscene == "DE" or pscene == "NE":
        rowHeight = 100
        isRoof = False
        if not oppress:
            print("已设置场地为五行")
    elif pscene == "RE" or pscene == "ME":
        rowHeight = 85
        if not oppress:
            print("已设置场地为天台")
        isRoof = True
    else:
        if not oppress:
            print("该场地不支持。")


def intersectCircRect(cirX, cirY, radius, rectX, rectY, rectW, rectH):
    X = rectX if cirX < rectX else (
        rectX + rectW if cirX > rectX + rectW else cirX)
    Y = rectY if cirY < rectY else (
        rectY + rectH if cirY > rectY + rectH else cirY)
    return ((cirX - X) ** 2 + (cirY - Y) ** 2) <= radius ** 2


def calcImp(xg, yg, rnd, dl, stackHigher=False, isIced=False, verbosity=1):
    if isRoof:
        return calcRoofImp(xg, yg, rnd, dl, stackHigher, isIced, verbosity)
    if (xg < 401) or (rnd != 0 and xg < 501):
        if verbosity >= 1:
            print("Invalid paramters.")
        return -1, -1, True, (-1)
    alreadyEat, earliestEatTime, damage = False, -1, 0
    earliestIceTime = -1
    eatLoop = 4 if not isIced else 8
    time = 106 if not isIced else 211
    if time > dl:
        if verbosity >= 2:
            print("Too early.")
        return -1, -1, True, (-1)
    g, vx, vy, x, y, h, state, existTime = -0.05, -3, (xg - 360 - rnd) / 120, xg - 133, yg, 88, 71, 0
    if stackHigher:
        vy += g
        x, h, existTime = x + vx, h + vy, existTime + 1
    while time < dl:
        if state == 71:
            vy += g
            x, h, existTime = x + vx, h + vy, existTime + 1
            time += 1
            if int(h) < 0:
                state = 72
                h = 0
                countDown = 25 if not isIced else 50
        elif state == 72:
            countDown -= 1
            existTime += 1
            time += 1
            if countDown == 0:
                state = 0
                alreadyEat = (existTime % eatLoop == 0)
                if alreadyEat:
                    earliestEatTime = time
        elif state == 0:
            existTime += 1
            time += 1
            if earliestIceTime == -1:
                earliestIceTime = time
            if existTime % eatLoop == 0:
                if not alreadyEat:
                    alreadyEat = True
                    earliestEatTime = time
                if alreadyEat:
                    damage = (time - earliestEatTime) // eatLoop * 4 + 4
                if damage >= 300:
                    if verbosity >= 2:
                        print("Damage too large.")
                    break
        else:
            if verbosity >= 1:
                print("Unexpected Error.")
            return -1, -1, True, (-1)
    return int(x), int(y - h), alreadyEat, (earliestEatTime, damage, earliestIceTime, h, eatLoop)


def calcRoofImp(xg, yg, rnd, dl, stackHigher=False, isIced=False, verbosity=1):
    if (xg < 401) or (rnd != 0 and xg < 501):
        if verbosity >= 1:
            print("Invalid paramters.")
        return -1, -1, True, (-1)
    alreadyEat, earliestEatTime, damage = False, -1, 0
    earliestIceTime = -1
    eatLoop = 4 if not isIced else 8
    time = 106 if not isIced else 211
    if time > dl:
        if verbosity >= 2:
            print("Too early.")
        return -1, -1, True, (-1)
    g, vx, vy, x, y, h, state, existTime = -0.05, -3, (xg - 360 - 180 - rnd) / 120, xg - 133, yg, 88, 71, 0
    if stackHigher:
        vy += g
        x, h, existTime = x + vx, h + vy, existTime + 1
        yshift = 0 if x >= 400 else (400 - x) / 4
        real_h = h + yshift
    while time < dl:
        if state == 71:
            vy += g
            x, h, existTime = x + vx, h + vy, existTime + 1
            yshift = 0 if x >= 400 else (400 - x) / 4
            real_h = h + yshift
            time += 1
            if int(real_h) < 0:
                state = 72
                h = 0
                real_h = 0
                countDown = 25 if not isIced else 50
        elif state == 72:
            countDown -= 1
            existTime += 1
            time += 1
            if countDown == 0:
                state = 0
                alreadyEat = (existTime % eatLoop == 0)
                if alreadyEat:
                    earliestEatTime = time
        elif state == 0:
            existTime += 1
            time += 1
            if earliestIceTime == -1:
                earliestIceTime = time
            if existTime % eatLoop == 0:
                if not alreadyEat:
                    alreadyEat = True
                    earliestEatTime = time
                if alreadyEat:
                    damage = (time - earliestEatTime) // eatLoop * 4 + 4
                if damage >= 300:
                    if verbosity >= 2:
                        print("Damage too large.")
                    break
        else:
            if verbosity >= 1:
                print("Unexpected Error.")
            return -1, -1, True, (-1)
    shift = 0 if x >= 400 else (400 - x)/4.0
    return int(x), int(y + shift - real_h), alreadyEat, (earliestEatTime, damage, earliestIceTime, real_h, eatLoop)


def doom(row, col):
    return col * colWidth, 120 + (row-1) * rowHeight, 250


def cob(row, col, paoCol=None, paoRow=None):
    x = int(col * colWidth)
    targetX = (x - 7) if (x >= 7) else x - 6
    if not isRoof:
        return targetX, 120 + (row-1) * rowHeight, 115
    else:
        if paoCol is None:
            print("屋顶场地需指定炮尾所在列.")
            return 0, 0, 0
        y = 209 + (row - 1) * rowHeight
        if x <= 206:
            step1 = 0
        elif x >= 527:
            step1 = 5
        else:
            step1 = (x - 127) // 80
        y -= step1 * 20
        if paoCol == 1:
            leftEdge = 87
            rightEdge = 524
            step2Shift = 0
        elif paoCol >= 7:
            leftEdge = 510
            rightEdge = 523
            step2Shift = 5
        else:
            leftEdge = 80 * paoCol - 13
            rightEdge = 524
            step2Shift = 5
        if x <= leftEdge:
            step2 = 0
        elif x >= rightEdge:
            step2 = (rightEdge - leftEdge + 3) // 4 - step2Shift
        else:
            step2 = (x - leftEdge + 3) // 4 - step2Shift
        y -= step2
        if (x == leftEdge) and (paoCol in (2, 3, 4, 5, 6)):
            if paoRow is None:
                print("特殊落点，需要指定炮所在行.")
                return 0, 0, 0
            if paoRow in (3, 4, 5):
                y += 5
            if paoRow == 3 and paoCol == 6:
                y -= 5
        y = 0 if y < 0 else y
        return targetX, y, 115


def judge(xgInfo, dl, rows, explodeInfo, isIced=False, verbosity=1):
    count = 0
    eatCount = 0
    missCount = 0
    totalDamage = 0
    if isinstance(xgInfo, list):
        if len(xgInfo) > 1:
            xgFast, xgSlow = xgInfo
        else:
            xgFast, xgSlow = xgInfo[0], xgInfo[0]
    else:
        xgFast, xgSlow = xgInfo, xgInfo
    explodeX, explodeY, radius = explodeInfo
    for xg in range(xgFast, xgSlow+1):
        if xg <= 400:
            continue
        for rnd in range(0, 101):
            if 401 <= xg <= 500 and rnd != 0:
                continue
            for stackHeight in [True, False]:
                for row in rows:
                    count += 1
                    impX, impY, eat, _ = calcImp(
                        xg, (50 if not isRoof else 40) + (row-1) * rowHeight, rnd, dl, stackHeight, isIced, verbosity)
                    if eat:
                        eatCount += 1
                        totalDamage += _[1]
                        if (verbosity == 1 and eatCount <= 5) or verbosity >= 2:
                            print("Eat:", [xg, rnd, dl, stackHeight, row, impX, impY, eat, _])
                        elif verbosity == 1 and eatCount == 6:
                            print("...")
                    if not intersectCircRect(explodeX, explodeY, radius, impX + 36, impY, 42, 115):
                        missCount += 1
                        if (verbosity == 1 and missCount <= 5) or verbosity >= 2:
                            print("Not Intercepted:", [xg, rnd, dl, stackHeight, row, impX, impY, eat, _])
                        elif verbosity == 1 and missCount == 6:
                            print("...")
    if verbosity >= 1:
        print("Eat/Miss/All: " + str(eatCount) + "/" + str(missCount) +
              "/" + str(count) + "; AvgDamage: " + str(totalDamage / count))
    return missCount == 0 and eatCount == 0


def iceKill(xgInfo, rows, isIced=True, verbosity=1):
    count = 0
    xgFast, xgSlow = xgInfo
    iceTimes = []
    eatTimes = []
    for xg in range(xgFast, xgSlow+1):
        if xg <= 400:
            continue
        for rnd in range(0, 101):
            if 401 <= xg <= 500 and rnd != 0:
                continue
            for stackHeight in [True, False]:
                for row in rows:
                    count += 1
                    impX, impY, eat, _ = calcImp(
                        xg, 50 + (row-1) * rowHeight, rnd, delayMustFallen, stackHeight, isIced, verbosity)
                    assert eat
                    eatTimes.append(_[0])
                    iceTimes.append(_[2])
    earliestIceTime = max(iceTimes)
    eatLoop = 8 if isIced else 4
    totalDamage = (earliestIceTime * count - sum(eatTimes)) // eatLoop * 4 + count * 4
    avgDamage = totalDamage / count
    if verbosity >= 1:
        print("IceTime: " + str(earliestIceTime) + "; All:" +
              str(count) + "; AvgDamage: " + str(avgDamage))
    return earliestIceTime

def findMaxDelay(xRange, rows, pR, paoCol, isIced=False, step=1, roofPaoCol=None): # TODO
    if isRoof and roofPaoCol is None:
        print("屋顶场地需要指定炮尾所在列")
        return -1
    xgInfo = []
    if not isinstance(xRange, list):
        xgInfo.append(xRange)
    else:
        xgInfo = xRange[:2]
    xgRows = []
    if not isinstance(rows, list):
        xgRows.append(rows)
    else:
        xgRows = rows
    paoRow = 0
    if isinstance(pR, list):
        paoRow = pR[0]
    else:
        paoRow = pR
    if step <= 0:
        raise Exception()
    dl = 107 if not isIced else 212
    paoLo, paoHi = paoCol
    paoLo = int(paoLo * 80)
    paoHi = int(paoHi * 80)
    resultDelay = -1
    resultX = -1
    paoX = paoLo
    while paoX <= paoHi:
        maxDelay = -1
        start = -1
        for d in range(dl, dl + 100):
            if judge(xgInfo[0], d, xgRows, cob(paoRow, paoX/80.0, roofPaoCol), isIced, 0) and \
                (len(xgInfo) == 1 or judge(xgInfo[1], d, xgRows, cob(paoRow, paoX/80.0, roofPaoCol), isIced, 0)):
                start = d
                break
        if start != -1:
            for d in range(start + 1, start + 100):
                if not judge(xgInfo[0], d, xgRows, cob(paoRow, paoX/80.0, roofPaoCol), isIced, 0) or \
                    (len(xgInfo) > 1 and not judge(xgInfo[1], d, xgRows, cob(paoRow, paoX/80.0, roofPaoCol), isIced, 0)):
                    maxDelay = d - 1
                    break
        if maxDelay > resultDelay:
            resultDelay = maxDelay
            resultX = paoX
        paoX += step
    print("最大延迟:", resultDelay)
    print("落点:", str(resultX/80.0)+"列")
    return resultDelay, resultX/80.0


def delay(xRange, rows, paoInfo, isIced=False, exact=False): # TODO
    xgInfo = []
    if not isinstance(xRange, list):
        xgInfo.append(xRange)
    else:
        xgInfo = xRange[:2]
    return minDelay(xgInfo, rows, paoInfo, isIced, exact), maxDelay(xgInfo, rows, paoInfo, isIced, exact)


def maxDelay(xRange, rows, paoInfo, isIced=False, exact=False):
    xgInfo = []
    if not isinstance(xRange, list):
        xgInfo.append(xRange)
    else:
        xgInfo = xRange[:2]
    if exact and len(xgInfo) == 1:
        xgInfo.append(xgInfo[0])
    xgRows = []
    if not isinstance(rows, list):
        xgRows.append(rows)
    else:
        xgRows = rows
    x, _, rd = paoInfo
    dl = 107 if not isIced else 212
    if x <= 400 and rd <= 115 and not exact and xgInfo[0] >= 600: # TODO
        dl += 80
    upper = dl + 200
    if rd <= 115 and not exact:
        upper = dl + 120
    found = False
    for d in range(dl, upper):
        if not exact:
            if not judge(xgInfo[0], d, xgRows, paoInfo, isIced, 0) or \
                (len(xgInfo) > 1 and not judge(xgInfo[1], d, xgRows, paoInfo, isIced, 0)):
                if found:
                    print("最大延迟:", d - 1, "("+str(dl)+"~"+str(upper)+")")
                    return d - 1
            else:
                found = True
        else:
            if not judge([xgInfo[0], xgInfo[1]], d, xgRows, paoInfo, isIced, 0):
                if found:
                    print("最大延迟（精确）:", d - 1, "("+str(dl)+"~"+str(upper)+")")
                    return d - 1
            else:
                found = True
    if not exact:
        if not found:
            print("最大延迟: 全部失败"+" ("+str(dl)+"~"+str(upper)+")")
        else:
            print("最大延迟: 全部成功"+" ("+str(dl)+"~"+str(upper)+")")
    else:
        if not found:
            print("最大延迟（精确）: 全部失败"+" ("+str(dl)+"~"+str(upper)+")")
        else:
            print("最大延迟（精确）: 全部成功"+" ("+str(dl)+"~"+str(upper)+")")
    return dl + 99


def minDelay(xRange, rows, paoInfo, isIced=False, exact=False):
    xgInfo = []
    if not isinstance(xRange, list):
        xgInfo.append(xRange)
    else:
        xgInfo = xRange[:2]
    if exact and len(xgInfo) == 1:
        xgInfo.append(xgInfo[0])
    xgRows = []
    if not isinstance(rows, list):
        xgRows.append(rows)
    else:
        xgRows = rows
    x, _, rd = paoInfo
    dl = 107 if not isIced else 212
    if x <= 400 and rd <= 115 and not exact and xgInfo[0] >= 600:
        dl += 80
    upper = dl + 200
    if rd <= 115 and not exact:
        upper = dl + 100
    for d in range(dl, upper):
        if not exact:
            if judge(xgInfo[0], d, xgRows, paoInfo, isIced, 0) and \
                (len(xgInfo) == 1 or judge(xgInfo[1], d, xgRows, paoInfo, isIced, 0)):
                print("最小延迟:", d, "("+str(dl)+"~"+str(upper)+")")
                return d
        else:
            if judge([xgInfo[0], xgInfo[1]], d, xgRows, paoInfo, isIced, 0):
                print("最小延迟（精确）:", d, "("+str(dl)+"~"+str(upper)+")")
                return d
    if not exact:
        print("最小延迟: 全部失败"+" ("+str(dl)+"~"+str(upper)+")")
    else:
        print("最小延迟（精确）: 全部失败"+" ("+str(dl)+"~"+str(upper)+")")
    return -1

def getGargDisplacementFast(time):
    if int(time) + 1 >= len(gf):
        raise ValueError("激活时机过晚")
    l, r = int(time), int(time) + 1
    return (gf[l] * (r - time) + gf[r] * (time - l)) / 32768.0


def getGargDisplacementSlow(time):
    if int(time) + 1 >= len(gf):
        raise ValueError("激活时机过晚")
    l, r = int(time), int(time) + 1
    return (gs[l] * (r - time) + gs[r] * (time - l)) / 32768.0


def getGargPos(walkTime):
    fastTime, slowTime = walkTime
    return [int(845 - getGargDisplacementFast(fastTime)), int(854 - getGargDisplacementSlow(slowTime))]


def pos(iT, paoTime=None, oppress=False):
    if paoTime is None:
        iT, paoTime = 0, iT
    iceTime = []
    if not isinstance(iT, list):
        iceTime.append(iT)
    else:
        iceTime = iT
    iceTime = sorted(filter(lambda x: 0 < x <= paoTime, iceTime))
    iceTime.append(paoTime + 1)
    slowTotal = 0
    fastTotal = 0
    lastTick = None
    doubleIce = False
    for t in iceTime:
        if lastTick is None:
            slowTotal += t - 1
            fastTotal += t - 1
        else:
            diff = t - lastTick
            slowTotal += max(diff - (599 if not doubleIce else 399), 0) / 2.0 + max((diff - 1999) / 2.0, 0)
            fastTotal += max(diff - (399 if not doubleIce else 299), 0) / 2.0 + max((diff - 1999) / 2.0, 0)
            doubleIce = (diff <= 1999)
        lastTick = t
    walkTime = [fastTotal, slowTotal]
    if not oppress:
        print(getGargPos(walkTime))
        print(cleandoc("""
        巨人举锤坐标参考：
        8普通 - 680
        8炮 - 670
        7普通 - 600
        7炮 - 590
        6普通 - 520
        6炮 - 510
        （高坚果为普通+20，南瓜则再+10）
        """))
    return getGargPos(walkTime)


def walk(wt):
    walkTime = []
    if not isinstance(wt, list):
        walkTime.append(wt)
    else:
        walkTime = wt
    fast = 845
    slow = 854
    for w in walkTime:
        fast -= getGargDisplacementFast(w)
        slow -= getGargDisplacementSlow(w)
    print([int(fast), int(slow)])
    print(cleandoc("""
    巨人举锤坐标参考：
    8普通 - 680
    8炮 - 670
    7普通 - 600
    7炮 - 590
    6普通 - 520
    6炮 - 510
    （高坚果为普通+20，南瓜则再+10）
    """))
    return [int(fast), int(slow)]


def getIceTimeDesc(iceTime):
    if len(iceTime) == 0:
        return "不用冰"
    elif len(iceTime) == 1:
        return str(iceTime[0])+"冰"
    else:
        return str(iceTime)+"冰"


iceTime, paoTime = [], 225

def main():
    global iceTime
    global paoTime
    line = input("\n>> ")
    try:
        if line == "exit" or line == "quit":
            sys.exit()
        elif line == "help":
            print(helpText)
        elif line.upper() in ["DE", "NE", "PE", "FE", "RE", "ME"]:
            scene(line.upper())
        elif line.startswith("wave"):
            params = line.split()
            if len(params) == 1:
                print("当前设置:", getIceTimeDesc(iceTime), str(paoTime)+"激活")
                print("巨人坐标范围:", pos(iceTime, paoTime, oppress=True))
            elif len(params) == 2:
                if int(params[1]) <= 0:
                    print("意外的输入。激活时机应为正数。")
                    return
                iceTime = []
                paoTime = int(params[1])
                gargPos = pos(iceTime, paoTime, oppress=True)
                if gargPos[1] > 817:
                    print("警告：此时机无法全伤巨人。")
                print("修改完毕。当前设置:", getIceTimeDesc(iceTime), str(paoTime)+"激活")
                print("巨人坐标范围:", gargPos)
            elif len(params) >= 3:
                if int(params[1]) > 0:
                    if int(params[1]) > int(params[2]):
                        print("意外的输入。激活时机不能早于冰时机。")
                        return
                if int(params[2]) <= 0:
                    print("意外的输入。激活时机应为正数。")
                    return
                iceTime = [int(x) for x in params[1:-1]]
                paoTime = int(params[-1])
                gargPos = pos(iceTime, paoTime, oppress=True)
                if gargPos[1] > 817:
                    print("警告：此时机无法全伤巨人。")
                print("修改完毕。当前设置:", getIceTimeDesc(iceTime), str(paoTime)+"激活")
                print("巨人坐标范围:", gargPos)
        elif line.startswith("hit"):
            params = line.split()
            if isRoof:
                if len(params) < 2:
                    print("意外的输入。屋顶场地需要指定炮尾所在列。")
                    return
                paoCol = int(params[1])
                if paoCol < 1 or paoCol > 8:
                    print("意外的输入。炮尾所在列只能输入1~8。")
                    return
            if (isRoof and len(params) >= 3) or (not isRoof and len(params) >= 2):
                extra = int(params[2]) if isRoof else int(params[1])
                if extra <= 0:
                    print("意外的输入。延迟必须为正数。")
                    return
                gargPos = pos(iceTime, paoTime + extra, oppress=True)
                print("延迟炮生效时机:", paoTime + extra)
            else:
                gargPos = pos(iceTime, paoTime, oppress=True)
            if isRoof:
                dist = windPaoDist[paoCol - 1]
            else:
                dist = [118, 125] if rowHeight == 85 else [111, 125]
            print("巨人坐标范围:", gargPos)
            if not isRoof:
                print("全伤本行&下行:", str(gargPos[1]-dist[1])+" ("+str((gargPos[1]-dist[1])/80.0)+"列)")
                print("全伤三行:", str(gargPos[1]-dist[0])+" ("+str((gargPos[1]-dist[0])/80.0)+"列)")
            else:
                print("全伤上行:", str(gargPos[1]-dist[0])+" ("+str((gargPos[1]-dist[0])/80.0)+"列)")
                print("全伤本行:", str(gargPos[1]-dist[1])+" ("+str((gargPos[1]-dist[1])/80.0)+"列)")
                print("全伤下行:", str(gargPos[1]-dist[2])+" ("+str((gargPos[1]-dist[2])/80.0)+"列)")
        elif line.startswith("nohit"):
            params = line.split()
            if isRoof:
                if len(params) < 2:
                    print("意外的输入。屋顶场地需要指定炮尾所在列。")
                    return
                paoCol = int(params[1])
                if paoCol < 1 or paoCol > 8:
                    print("意外的输入。炮尾所在列只能输入1~8。")
                    return
            if (isRoof and len(params) >= 3) or (not isRoof and len(params) >= 2):
                extra = int(params[2]) if isRoof else int(params[1])
                if extra <= 0:
                    print("意外的输入。延迟必须为正数。")
                    return
                gargPos = pos(iceTime, paoTime + extra, oppress=True)
                print("延迟炮生效时机:", paoTime + extra)
            else:
                gargPos = pos(iceTime, paoTime, oppress=True)
            if isRoof:
                dist = windPaoDist[paoCol - 1]
            else:
                dist = [118, 125] if rowHeight == 85 else [111, 125]
            print("巨人坐标范围:", gargPos)
            if not isRoof:
                print("不伤本行&下行:", str(gargPos[0]-dist[1]-1)+" ("+str((gargPos[0]-dist[1]-1)/80.0)+"列)")
                print("不伤上行:", str(gargPos[0]-dist[0]-1)+" ("+str((gargPos[0]-dist[0]-1)/80.0)+"列)")
            else:
                print("不伤上行:", str(gargPos[0]-dist[0]-1)+" ("+str((gargPos[0]-dist[0]-1)/80.0)+"列)")
                print("不伤本行:", str(gargPos[0]-dist[1]-1)+" ("+str((gargPos[0]-dist[1]-1)/80.0)+"列)")
                print("不伤下行:", str(gargPos[0]-dist[2]-1)+" ("+str((gargPos[0]-dist[2]-1)/80.0)+"列)")
        elif line.startswith("delay "):
            params = line.split()
            paoCol = None
            if isRoof:
                if len(params) <= 2:
                    print("意外的输入。屋顶场地需要指定炮尾所在列。")
                    return
                paoCol = int(params[1])
                if paoCol < 1 or paoCol > 8:
                    print("意外的输入。炮尾所在列只能输入1~8。")
                    return
                params.pop(1)
            if len(params) == 1:
                print("意外的输入。需要指定落点。")
                return
            if len(params) >= 2:
                paoX = float(params[1])
                if paoX < 0 or paoX >= 10:
                    print("意外的输入。落点超出有效范围（0~9.9875）。")
                    return
                if len(params) >= 3:
                    rows = int(params[2])
                    if not rows in [1, 2, 3]:
                        print("意外的输入。拦截行数应为1~3。")
                        return
                else:
                    rows = 2
                isIced = (iceTime != [] and iceTime[-1] + 1999 > paoTime)
                paoRow = 3
                xgRow = list(range(5 - rows, 5))
                gargPos = pos(iceTime, paoTime, oppress=True)
                minDelay_, maxDelay_ = delay(gargPos, xgRow, cob(paoRow, paoX, paoCol), isIced)
                if iceTime != [] and iceTime[-1] + 1999 <= paoTime + maxDelay_:
                    print("警告：拦截过程中巨人/小鬼恢复原速。请自行换算拦截时机。")
        elif line == "version":
            print("BrainVsZombies General Interception Calculator ver 1.2 by Elovi, Crescendo, Reisen")
        else:
            eval(line)
    except Exception as e:
        print(e)
        print("意外的输入。输入help查看帮助。")

if __name__ == "__main__":
    print(welcomeText)
    scene("PE", True)
    while True:
        main()
