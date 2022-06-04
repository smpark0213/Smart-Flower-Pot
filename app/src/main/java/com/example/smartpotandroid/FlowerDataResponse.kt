package com.example.smartpotandroid

import com.google.gson.annotations.SerializedName

data class FlowerDataResponse(
    @SerializedName("code") val code: Int,
    @SerializedName("msg") val message: Array<FlowerData>,
    @SerializedName("success") val isSuccess: Boolean
)