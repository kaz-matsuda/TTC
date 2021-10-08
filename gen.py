# number_of_applicant人分の preferenceリストを作成するプログラム
# 作成されるpreferenceデータのファイル名を'test.csv'としています

f = open('test.csv', 'w')

number_of_applicant = 800 # 交換希望者数
number_of_slot = 56  # 総スロット数

import random

random.seed(100)

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
                        
                

while i <= number_of_applicant: # 人数分のpreferenceリストを作成
        originslotnumber = random.randint(1,number_of_slot) # 元々の予約スロットに対応する数字
        print(originslotnumber)
        marunumber = 3*(random.randint(2, 6)) # ◯の個数, 6・9・12・15・18個のいずれか
        #print(marunumber)
        marunumberlist = rand_ints_nodup(1,number_of_slot,marunumber)
        marunumberlist.sort()
        print(marunumberlist)
        sankakunumber = 3*(random.randint(2, 6)) # △の個数, 6・9・12・15・18個のいずれか
        print(sankakunumber)
        # △のスロットのリストを作成する
        sankakunumberlist = makesankaku(1, number_of_slot, sankakunumber)
        sankakunumberlist.sort()
        print(sankakunumberlist)

        
        preferencelist.append(originslotnumber)
        #print("preferencelist=")
        while k <= number_of_slot:
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
        while m <= number_of_slot + 1:
                if m < number_of_slot + 1:
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

f.close()
 
