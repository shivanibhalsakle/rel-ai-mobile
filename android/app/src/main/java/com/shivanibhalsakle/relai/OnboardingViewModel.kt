package com.shivanibhalsakle.relai

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shivanibhalsakle.relai.network.BudgetBandBody
import com.shivanibhalsakle.relai.network.OnboardingRequestBody
import com.shivanibhalsakle.relai.network.RetrofitClient
import com.shivanibhalsakle.relai.network.WorkspaceNeedsBody
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

sealed interface OnboardingSubmitState {
    data object Idle : OnboardingSubmitState
    data object Loading : OnboardingSubmitState
    data object Success : OnboardingSubmitState
    data class Error(val message: String) : OnboardingSubmitState
}

class OnboardingViewModel : ViewModel() {

    var activitiesText by mutableStateOf("")
    var budgetMin by mutableStateOf("")
    var budgetMax by mutableStateOf("")
    var budgetPeriod by mutableStateOf("month")
    var maxTravelMinutes by mutableStateOf("")
    var travelMode by mutableStateOf("walk")
    var minRating by mutableStateOf("")
    var wifiNeeded by mutableStateOf(false)
    var outletsNeeded by mutableStateOf(false)
    var quietNeeded by mutableStateOf(false)
    var foodNeeded by mutableStateOf(false)
    var workoutTimesText by mutableStateOf("")
    var indoorOutdoorPreference by mutableStateOf("either")

    private val _submitState = MutableStateFlow<OnboardingSubmitState>(OnboardingSubmitState.Idle)
    val submitState: StateFlow<OnboardingSubmitState> = _submitState

    fun submit() {
        _submitState.value = OnboardingSubmitState.Loading
        viewModelScope.launch {
            try {
                val request = OnboardingRequestBody(
                    activities = activitiesText.split(",").map { it.trim() }.filter { it.isNotEmpty() },
                    budgetBand = if (budgetMin.isNotBlank() && budgetMax.isNotBlank()) {
                        BudgetBandBody(min = budgetMin.toDouble(), max = budgetMax.toDouble(), period = budgetPeriod)
                    } else null,
                    maxTravelMinutes = maxTravelMinutes.toIntOrNull(),
                    travelMode = travelMode,
                    minRating = minRating.toDoubleOrNull(),
                    workspaceNeeds = WorkspaceNeedsBody(wifiNeeded, outletsNeeded, quietNeeded, foodNeeded),
                    preferredWorkoutTimes = workoutTimesText.split(",").map { it.trim() }.filter { it.isNotEmpty() },
                    indoorOutdoorPreference = indoorOutdoorPreference
                )
                RetrofitClient.apiService.submitOnboarding(request)
                _submitState.value = OnboardingSubmitState.Success
            } catch (e: Exception) {
                _submitState.value = OnboardingSubmitState.Error(e.message ?: "Failed to save preferences")
            }
        }
    }
}