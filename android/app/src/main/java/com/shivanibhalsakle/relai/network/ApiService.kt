package com.shivanibhalsakle.relai.network

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface ApiService {
    @GET("v1/me")
    suspend fun getMe(): MeResponse

    @GET("v1/onboarding")
    suspend fun getOnboardingStatus(): OnboardingStatusResponse

    @POST("v1/onboarding")
    suspend fun submitOnboarding(@Body request: OnboardingRequestBody): OnboardingResponseBody
}

data class MeResponse(val uid: String)

data class OnboardingStatusResponse(
    val onboardingCompleted: Boolean,
    val preferences: OnboardingRequestBody? = null
)

data class BudgetBandBody(
    val min: Double,
    val max: Double,
    val currency: String = "USD",
    val period: String
)

data class WorkspaceNeedsBody(
    val wifi: Boolean = false,
    val outlets: Boolean = false,
    val quiet: Boolean = false,
    val food: Boolean = false
)

data class OnboardingRequestBody(
    val activities: List<String> = emptyList(),
    val budgetBand: BudgetBandBody? = null,
    val maxTravelMinutes: Int? = null,
    val travelMode: String? = null,
    val minRating: Double? = null,
    val workspaceNeeds: WorkspaceNeedsBody = WorkspaceNeedsBody(),
    val preferredWorkoutTimes: List<String> = emptyList(),
    val indoorOutdoorPreference: String = "either"
)

data class OnboardingResponseBody(
    val status: String,
    val preferencesId: String
)

