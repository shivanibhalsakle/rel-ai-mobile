package com.shivanibhalsakle.relai.network

import retrofit2.http.GET

interface ApiService {
    @GET("v1/me")
    suspend fun getMe(): MeResponse

    @GET("v1/onboarding")
    suspend fun getOnboardingStatus(): OnboardingStatusResponse
}

data class MeResponse(val uid: String)

data class OnboardingStatusResponse(val onboardingCompleted: Boolean)