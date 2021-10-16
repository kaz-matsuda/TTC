# number_of_applicant人分の preferenceリストを作成するプログラム
# 作成されるpreferenceデータのファイル名を'test.csv'としています

f = open('test.csv', 'w')

number_of_applicant = 800 # 交換希望者数
number_of_slot = 51  # 総スロット数

import math
import random

random.seed(100)

i = 1
j = 1
k = 1
m = 1
originslotnumber = 99
preferencelist = []
marunumberlist = []

# Generates a non-duplicate sequence of integers randomly taken from [a, b];
# k bounds the length of the generated list: the length is min(1+b-a, k).
# The numbers listed in the final argument is removed from the candidate.
def rand_ints_nodup_avoiding(a, b, k, avoid=[]):
        ns = list(set(range(a,b+1)) - set(avoid))
        random.shuffle(ns)
        return ns[:k]

def rand_ints_nodup(a, b, k):
        return rand_ints_nodup_avoiding(a,b,k,[])

while i <= number_of_applicant: # 人数分のpreferenceリストを作成
        originslotnumber = random.randint(1,number_of_slot) # 元々の予約スロットに対応する数字
        print(originslotnumber)
        #marunumber = math.floor(random.expovariate(1.0/15.0) + 1)
        marunumber = math.floor(random.gauss(15, 0.2))
        #print(marunumber)
        marunumberlist = rand_ints_nodup(1,number_of_slot,marunumber)
        marunumberlist.sort()
        print(marunumberlist)
        sankakunumber = math.floor(random.expovariate(1))
        print(sankakunumber)
        # △のスロットのリストを作成する
        sankakunumberlist = rand_ints_nodup_avoiding(1, number_of_slot, sankakunumber, marunumberlist)
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
 
