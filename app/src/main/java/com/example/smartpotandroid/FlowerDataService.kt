package com.example.smartpotandroid

import android.util.Log
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class FlowerDataService() {

    lateinit var flower: FlowerData

    fun getDatas() {
        val flowerPotService = getRetrofit().create(FlowerDataRetrofitInterfaces::class.java)

        flowerPotService.getDatas().enqueue(object : Callback<FlowerDataResponse> {
            override fun onResponse(
                call: Call<FlowerDataResponse>,
                response: Response<FlowerDataResponse>
            ) {
                if (response.isSuccessful && response.code() == 200) {
                    val flowerDataResponse: FlowerDataResponse = response.body()!!

                    flower = flowerDataResponse.message[0]

                    Log.d("flowerDataResponse", flower.toString())
                }
            }

            override fun onFailure(call: Call<FlowerDataResponse>, t: Throwable) {
                Log.d("flowerDataResponse", "FAIL", t)
            }
        })
    }
}