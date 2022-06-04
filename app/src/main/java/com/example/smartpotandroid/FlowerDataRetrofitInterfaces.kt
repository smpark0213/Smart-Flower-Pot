package com.example.smartpotandroid

import retrofit2.Call
import retrofit2.http.GET

interface FlowerDataRetrofitInterfaces {
    @GET("/flowerpot")
    fun getDatas():Call<FlowerDataResponse>
}