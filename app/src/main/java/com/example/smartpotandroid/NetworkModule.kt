package com.example.smartpotandroid

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

// 연결할 서버의 주소
const val BASE_URL = ""

fun getRetrofit(): Retrofit {
    val retrofit = Retrofit.Builder().baseUrl(BASE_URL)
        .addConverterFactory(GsonConverterFactory.create()).build()

    return retrofit
}