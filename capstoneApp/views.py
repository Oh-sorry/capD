from select import select
from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.views import View
from django.core import serializers

from .models import *
from capstoneApp.serializers import UserinfoSerializer, Item_ListSerializer, RefrigeratorItemSerializer, \
    RecipeListSerializer
from ml import predict_0704

import numpy as np
import subprocess
import json
import pandas as pd
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
import pymysql.cursors


def index():
    return HttpResponse("안녕하세요 pybo에 오신것을 환영합니다.")


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        if userinfo.objects.filter(userid=data['userid']).exists():
            obj = userinfo.objects.get(userid=data['userid'])
            print(obj)
            if obj.password == data['password']:
                str = data['userid']
                print(str)
                return JsonResponse({'code': '0000', 'msg': '로그인 성공'}, status=200)
            else:
                return JsonResponse({'code': '0001', 'msg': '비밀번호 불일치'}, status=200)
        else:
            return JsonResponse({'code': '0002', 'msg': '아이디가 존재하지 않음'}, status=200)
    else:
        return JsonResponse({'code': '0003', 'msg': '통신이 원할하지않습니다.'}, status=500)


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        if userinfo.objects.filter(userid=data['userid']).exists():
            return JsonResponse({'code': '0000', 'msg': '이미 등록된 아이디가 있습니다.'}, status=200)
        elif len(data['password']) < 6:
            return JsonResponse({'code': '0001', 'msg': '비밀번호를 6자 이상으로 설정해주세요.'}, status=200)
        else:
            print(data)
            serializer = UserinfoSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'code': '0002', 'msg': '회원가입에 성공하였습니다.'}, status=200)
    else:
        return JsonResponse({'code': '1231', 'msg': '포스트로 보낵라...'}, status=500)


@csrf_exempt
def textrunning(request):
    if request.method != 'POST':
        return JsonResponse({"msg": 'connection fail'}, status=500)

    else:
        """
        전송되는 데이터
        {   "user": {"userid": "test123"},
            "word": [
                        {"0":"[고추장][라라][어어][ㅋ]"},
				        {"1":"ㅁㄴㅇㅇㄴㅁㄴ"},
				        {"2":"[잘볶은][밀가루]"}
				    ]
		}
		이런모양임
        """
        # 요청받은 json 받음
        data = JSONParser().parse(request)
        # json에 있는 사용자의 id를 userid에 저장
        userid = data['userid']

        # json에서 word라는 배열 데이터를 testdata.json에 씀
        with open('ml/dataset/testdata/testdata.json', 'w', encoding='utf-8') as f:
            json.dump(data2['word'], f, ensure_ascii=False, indent=4)

        """
        앞에 0704.py는 실행시키는곳
        testdata.json에 지금 사진속 text들이 저장되있는데 그것을 모듈을 적용해시킴, 그러면 적용된json은 pre_data에 저장됨 
        """
        subprocess.run('python ml/predict_0704.py ml/dataset/testdata/testdata.json', shell=True)

        # 러닝을 돌린후 나온 데이터는 predict_list에 저장이 됌.
        pre_data = 'ml/dataset/predict_data/predict_list(*).json'

        """
        pre_data에 있는 정보들 DB랑 비교하여, 저장된 아이탬이면, refrigerator_item에 추가하기.
        """
        with open(pre_data, "r") as f:
            data = json.load(f)

        """
        차후, 모듈을거친 데이터를 응답으로 보내줄것
        그후, 사용자가 확인버튼을누르면 json데이터를 보내주고
        그데이터를 짜로 save해주는 함수를 만들기위해 밑에미리 작성해둠.!
        """
        # result_test = {"item_list": data}
        # print(result_test)
        # return JsonResponse(result_test, status=200)

        # pre_data의 길이만큼 반복을수행
        # data는 지금 배열형식[{},{},{}]
        for a in range(0, len(data)):
            result = {'userid': userid['userid']}

            # pre_data에 있는 재료가 개발자가 저장한DB의 아이탬명들과 일치하는지의 여부를 체크
            if item_list.objects.filter(item_name=data[a]["item_name"]).exists():
                print("item_list에 아이탬이존재함")
                # 냉장고에 이미있는 아이탬일경우를 체크
                if refrigerator_item.objects.filter(item_name=data[a]['item_name'], userid=result['userid']).exists():
                    obj = refrigerator_item.objects.get(item_name=data[a]['item_name'], userid=result['userid'])
                    obj.item_counts += 1
                    obj.save()
                    # refrigerator_item.objects.filter(item_name=data[a]['item_name']).update(item_counts)
                else:
                    print("냉장고에는 아이탬이 존재하지않음")
                    result['item_name'] = data[a]['item_name']
                    print(result)
                    result['insert_date'] = ''
                    result['item_counts'] = 1
                # 왜내가 한개씩 저장하고, 또 초기화해서 저장하게했는지는 모르겠지만.. 건들진않겠다....
                # {'userid':'사용자아이디','item_name':'학습되서나온 item명'}이 저장
                serializer = RefrigeratorItemSerializer(data=result)
                if serializer.is_valid():
                    serializer.save()
            else:
                print("없는데이터입니다")

        # 모두 저장하고, 잘됬으면 최종저장완료하고, 응답전송
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'code': '0000', "msg": '보내짐'}, status=200)
        else:
            return JsonResponse({'code': '0001', "msg": '보내지긴했지만 null'}, status=200)


# 내 냉장고 데이터 전송
@csrf_exempt
def getMyRefrigerator(request):
    data = JSONParser().parse(request)

    # 서버로 보낼 json객체
    result = {}

    # refrigerator_item 테이블에서 userid가 요청으로온id인 데이터들을 찾음
    datalist = refrigerator_item.objects.filter(userid=data['userid']).values()
    # item들을 담을 배열을 하나 생성
    total_item = []

    for a in datalist.values_list():
        # item에 이름,개수,날자를 넣어서 배열에넣어줌
        item = {"item_name": a[2], "item_date": a[3], "item_counts": a[4]}
        total_item.append(item)

    # result라는 json에 item이라는 명으로 []하나 만들어줘서 거기에 total_item배열을 넣음
    result["items"] = total_item

    # result to json
    json_val = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False, default=str)

    print(json_val)

    return JsonResponse(result, status=200)


@csrf_exempt
def getMyRecipe(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        datalist = refrigerator_item.objects.filter(userid=data['userid']).values()

        result = {}
        total_recipe_list = []

        # 재료들 하나하나 검사
        for i in datalist.values_list():
            # 재료가 레시피에서 중요도는 상 이면서, 그게 가지고있는 재료라면
            if recipe_item_list.objects.filter(item_name=i[2], item_importance='상').exists():
                obj = recipe_item_list.objects.filter(item_name=i[2], item_importance='상').values()
                for j in obj.values_list():
                    item = {'recipe_name': j[1]}
                    total_recipe_list.append(item)

        result['recipe_list'] = total_recipe_list
        # json_val = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False, default=str)
        # print(json_val)
        return JsonResponse(result, status=200)


@csrf_exempt
def saveItem(request):
    if request.method != 'POST':
        return JsonResponse({"msg": "not post"}, status=201)
    else:
        data = JSONParser().parse(request)
        userid = data['userid']
        result = {'userid': userid}
        print(result)

        for a in data['word']:
            # pre_data에 있는 재료가 개발자가 저장한DB의 아이탬명들과 일치하는지의 여부를 체크
            if item_list.objects.filter(item_name=a['item_name']).exists():
                print("item_list에 아이탬이존재함")
                # 냉장고에 이미있는 아이탬일경우를 체크
                if refrigerator_item.objects.filter(item_name=a['item_name'], userid=userid).exists():
                    obj = refrigerator_item.objects.get(item_name=a['item_name'], userid=result['userid'])
                    obj.item_counts += 1
                    obj.save()
                    # refrigerator_item.objects.filter(item_name=data[a]['item_name']).update(item_counts)
                else:
                    print("냉장고에는 아이탬이 존재하지않음")
                    result['item_name'] = a['item_name']
                    print(result)
                    result['insert_date'] = ''
                    result['item_counts'] = 1
                # 왜내가 한개씩 저장하고, 또 초기화해서 저장하게했는지는 모르겠지만.. 건들진않겠다....
                # {'userid':'사용자아이디','item_name':'학습되서나온 item명'}이 저장
                serializer = RefrigeratorItemSerializer(data=result)
                if serializer.is_valid():
                    serializer.save()
            else:
                print("없는데이터입니다")

        return JsonResponse({"msg": "save"}, status=200)
