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
            if obj.password == data['password']:
                str = data['userid']
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
        # 요청받은 json 받음
        data = JSONParser().parse(request)
        # json에 있는 사용자의 id를 userid에 저장
        userid = data['user']['userid']

        # json에서 word라는 배열 데이터를 testdata.json에 씀
        with open('ml/dataset/testdata/testdata.json', 'w', encoding='utf-8') as f:
            json.dump(data['word'], f, ensure_ascii=False, indent=4)

        subprocess.run('python ml/predict_0704.py ml/dataset/testdata/testdata.json', shell=True)

        pre_data = 'ml/dataset/predict_data/predict_list(*).json'

        """
        pre_data에 있는 정보들 DB랑 비교하여, 저장된 아이탬이면, refrigerator_item에 추가하기.
        """
        with open(pre_data, "r") as f:
            result_data = json.load(f)

        result = {}
        result['word'] = result_data
        return JsonResponse(result, status=200)


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
        if a[4] > 0:
            item = {"item_name": a[2], "item_date": a[3], "item_counts": a[4]}
            total_item.append(item)

        # item에 이름,개수,날자를 넣어서 배열에넣어줌

    # result라는 json에 item이라는 명으로 []하나 만들어줘서 거기에 total_item배열을 넣음
    result["items"] = total_item

    # result to json
    json_val = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False, default=str)

    return JsonResponse(result, status=200)


@csrf_exempt
def getMyRecipe(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        datalist = refrigerator_item.objects.filter(userid=data['userid']).values()

        # 상이 포함된 레시피는 아래 배열에 들어가게 됌.
        recipe_list = []

        for i in datalist.values_list():
            if refrigerator_item.objects.filter(item_counts=0, item_name=i[2]).exists():
                print("개수 0")
            else:
                if recipe_item_list.objects.filter(item_name=i[2], item_importance="상").exists():
                    obj = recipe_item_list.objects.filter(item_name=i[2], item_importance='상').values()
                    print(obj)
                    for j in obj.values_list():
                        recipe_list.append(j[1])

        point_list = []

        for i in recipe_list:
            a = 0
            for j in datalist.values_list():
                if refrigerator_item.objects.filter(item_name=j[2], item_counts=0).exists():
                    print("개수가 0개")
                elif recipe_item_list.objects.filter(item_name=j[2], recipe_name=i).exists():
                    obj = recipe_item_list.objects.filter(item_name=j[2], recipe_name=i).get()
                    a += obj.item_points
            a = a * 10
            points_json = {"recipe_name": i, "points": str(a)}
            point_list.append(points_json)
        result = {"recipe_list": point_list}

        return JsonResponse(result, status=200)


@csrf_exempt
def saveItem(request):
    if request.method != 'POST':
        return JsonResponse({"msg": "not post"}, status=201)
    else:
        data = JSONParser().parse(request)
        userid = data["user"]["userid"]
        result = {'userid': userid}
        for a in data['word']:
            # pre_data에 있는 재료가 개발자가 저장한DB의 아이탬명들과 일치하는지의 여부를 체크
            if item_list.objects.filter(item_name=a['item_name']).exists():
                # 냉장고에 이미있는 아이탬일경우를 체크
                if refrigerator_item.objects.filter(item_name=a["item_name"], userid=userid).exists():
                    obj = refrigerator_item.objects.get(item_name=a["item_name"], userid=result["userid"])
                    obj.item_counts += 1
                    obj.save()
                else:
                    result['item_name'] = a['item_name']
                    # result['insert_date'] = ''
                    result['item_counts'] = 1
                    serializer = RefrigeratorItemSerializer(data=result)
                    if serializer.is_valid():
                        serializer.save()
            else:
                print("없는데이터입니다")

        return JsonResponse({"msg": "save"}, status=200)


@csrf_exempt
def removeItem(request):
    if request.method != 'POST':
        return JsonResponse({"code": "0001"}, status=201)
    else:
        data = JSONParser().parse(request)
        if refrigerator_item.objects.filter(userid=data['userid'], item_name=data['item_name']).exists():
            obj = refrigerator_item.objects.filter(userid=data['userid'], item_name=data['item_name'])
            obj.delete()
            return JsonResponse({"code": "0000"}, status=200)


@csrf_exempt
def updateItem(request):
    if request.method != 'POST':
        return JsonResponse({"code": "0001"}, status=201)
    else:
        data = JSONParser().parse(request)
        if refrigerator_item.objects.filter(userid=data['userid'], item_name=data['old_name'],
                                            item_counts=data["old_count"]).exists():
            obj = refrigerator_item.objects.filter(userid=data['userid'], item_name=data['old_name'],
                                                   item_counts=data["old_count"])
            obj.update(item_counts=data['update_count'], item_name=data['update_name'])
            return JsonResponse({"code": "0000"}, status=200)


@csrf_exempt
def getRecipeProcess(request):
    if request.method != "POST":
        return JsonResponse({"code": "0001"}, status=201)
    else:
        data = JSONParser().parse(request)
        if recipe_process.objects.filter(recipe_name=data['recipename']).exists():
            RecipeProcess = recipe_process.objects.filter(recipe_name=data['recipename']).values()
            result_ary = []
            for i in RecipeProcess:
                json_datas = {"order": i['order'], "process": i['process']}
                result_ary.append(json_datas)

            need_items = []
            obj = recipe_item_list.objects.filter(recipe_name=data['recipename']).values()
            for i in obj:
                need_items.append(i['item_name_id'])
            print(need_items)
            total_result = {"need_items": need_items, "processlist": result_ary}
            return JsonResponse(total_result, status=200)
        else:
            return JsonResponse({"code": "0001"}, status=201)


@csrf_exempt
def useRecipe(request):
    if request.method != 'POST':
        return JsonResponse({"code": "0001"}, status=201)
    else:
        data = JSONParser().parse(request)
        recipe_items = recipe_item_list.objects.filter(recipe_name=data['recipename']).values_list('item_name',
                                                                                                   flat=True)
        for i in recipe_items:
            if refrigerator_item.objects.filter(userid=data['userid'], item_name=i).exists():
                obj = refrigerator_item.objects.get(userid=data['userid'], item_name=i)
                if obj.item_counts >= 0:
                    obj.item_counts -= 1
                    obj.save()

        return JsonResponse({"code": "0000"}, status=200)


@csrf_exempt
def userAddItem(request):
    if request.method != 'POST':
        return JsonResponse({"code": "0001"}, status=201)
    else:
        data = JSONParser().parse(request)
        userid = data["user"]["userid"]
        result = {'userid': userid}
        for a in data['items']:
            # pre_data에 있는 재료가 개발자가 저장한DB의 아이탬명들과 일치하는지의 여부를 체크
            if item_list.objects.filter(item_name=a['item_name']).exists():
                # 냉장고에 이미있는 아이탬일경우를 체크
                if refrigerator_item.objects.filter(item_name=a["item_name"], userid=userid).exists():
                    obj = refrigerator_item.objects.get(item_name=a["item_name"], userid=result["userid"])
                    cnt = a['item_count']
                    cnt = int(cnt)
                    obj.item_counts = obj.item_counts + cnt
                    obj.save()
                else:
                    result['item_name'] = a['item_name']
                    result['insert_date'] = ''
                    result['item_counts'] = a['item_count']
                    serializer = RefrigeratorItemSerializer(data=result)
                    if serializer.is_valid():
                        serializer.save()
            else:
                print("없는데이터입니다")

    return JsonResponse({"code": "0000"}, status=200)
