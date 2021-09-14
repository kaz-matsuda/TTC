# n人分の preferenceリストを作成するプログラム
#

f = open('test.csv', 'w')

import random

i = 1
j = 1
k = 1
m = 1
originslotnumber = 99
preferencelist = []
marunumberlist = []

# random function
def rand_ints_nodup(a, b, k):
        ns = []
        while len(ns) < k:
                n = random.randint(a, b)
                if not ((n in ns) or (n ==  originslotnumber)):
                        ns.append(n)
        return ns

def makesankaku(a, b, k):
        ns2 = []
        while len(ns2) < k:
                n = random.randint(a, b)
                if not ((n in ns2) or (n in marunumberlist) or (n == originslotnumber)):
                        ns2.append(n)
        return ns2
                        
                

while i <=100: # i人分の preferenceリストを作成
        originslotnumber = random.randint(1,78) # 元々の予約スロットに対応する数字
        print(originslotnumber)
        marunumber = random.randint(5, 20) # ◯の個数, 5以上20以下
        #print(marunumber)
        marunumberlist = rand_ints_nodup(1,78,marunumber)
        marunumberlist.sort()
        print(marunumberlist)
        sankakunumber = random.randint(5, 20) # △の個数, 5以上20以下
        print(sankakunumber)
        # △のスロットのリストを作成する
        sankakunumberlist = makesankaku(1, 78, sankakunumber)
        sankakunumberlist.sort()
        print(sankakunumberlist)

        
        preferencelist.append(originslotnumber)
        #print("preferencelist=")
        while k <= 78:
                if k == originslotnumber:
                        preferencelist.append(9)
                elif k in marunumberlist:
                        preferencelist.append(1)
                elif k in sankakunumberlist:
                        preferencelist.append(2)
                else:
                        preferencelist.append(3)
                k = k + 1
                  
        print(preferencelist)
        # test.txt に preferencelist を書き込む
        while m <= 79:
                if m < 79:
                        f.write(str(preferencelist[m-1]) + ',')
                else:
                        f.write(str(preferencelist[m-1]))
                m = m + 1
        
        f.write( '\n')
        preferencelist = []
        i = i + 1
        j = 1
        k = 1
        m = 1
        originslotnumber = 99
        print("\n")

f.write('end')

f.close()
 
