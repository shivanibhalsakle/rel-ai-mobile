package com.shivanibhalsakle.relai.network

import retrofit2.http.GET

interface ApiService {
    @GET("v1/me")
    suspend fun getMe(): MeResponse
}

data class MeResponse(val uid: String)