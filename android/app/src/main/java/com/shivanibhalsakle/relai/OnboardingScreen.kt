package com.shivanibhalsakle.relai

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun OnboardingScreen(
    modifier: Modifier = Modifier,
    viewModel: OnboardingViewModel = viewModel(),
    onOnboardingComplete: () -> Unit = {}
) {
    val submitState by viewModel.submitState.collectAsStateWithLifecycle()

    LaunchedEffect(submitState) {
        if (submitState is OnboardingSubmitState.Success) {
            onOnboardingComplete()
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text("Tell us your preferences")

        OutlinedTextField(
            value = viewModel.activitiesText,
            onValueChange = { viewModel.activitiesText = it },
            label = { Text("Activities (comma-separated, e.g. gym, yoga, climbing)") },
            modifier = Modifier.fillMaxWidth()
        )

        Text("Budget")
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(
                value = viewModel.budgetMin,
                onValueChange = { viewModel.budgetMin = it },
                label = { Text("Min") },
                modifier = Modifier.weight(1f)
            )
            OutlinedTextField(
                value = viewModel.budgetMax,
                onValueChange = { viewModel.budgetMax = it },
                label = { Text("Max") },
                modifier = Modifier.weight(1f)
            )
        }
        LabeledRadioGroup(
            label = "Budget period",
            options = listOf("month" to "Per month", "class" to "Per class"),
            selected = viewModel.budgetPeriod,
            onSelect = { viewModel.budgetPeriod = it }
        )

        OutlinedTextField(
            value = viewModel.maxTravelMinutes,
            onValueChange = { viewModel.maxTravelMinutes = it },
            label = { Text("Max travel time (minutes)") },
            modifier = Modifier.fillMaxWidth()
        )

        LabeledRadioGroup(
            label = "Travel mode",
            options = listOf("walk" to "Walk", "bike" to "Bike", "transit" to "Transit", "drive" to "Drive"),
            selected = viewModel.travelMode,
            onSelect = { viewModel.travelMode = it }
        )

        OutlinedTextField(
            value = viewModel.minRating,
            onValueChange = { viewModel.minRating = it },
            label = { Text("Minimum rating (0-5)") },
            modifier = Modifier.fillMaxWidth()
        )

        Text("Workspace needs")
        LabeledCheckbox("Wifi", viewModel.wifiNeeded) { viewModel.wifiNeeded = it }
        LabeledCheckbox("Outlets", viewModel.outletsNeeded) { viewModel.outletsNeeded = it }
        LabeledCheckbox("Quiet", viewModel.quietNeeded) { viewModel.quietNeeded = it }
        LabeledCheckbox("Food available", viewModel.foodNeeded) { viewModel.foodNeeded = it }

        OutlinedTextField(
            value = viewModel.workoutTimesText,
            onValueChange = { viewModel.workoutTimesText = it },
            label = { Text("Preferred workout times (comma-separated, e.g. morning, evening)") },
            modifier = Modifier.fillMaxWidth()
        )

        LabeledRadioGroup(
            label = "Indoor/outdoor preference",
            options = listOf("indoor" to "Indoor", "outdoor" to "Outdoor", "either" to "Either"),
            selected = viewModel.indoorOutdoorPreference,
            onSelect = { viewModel.indoorOutdoorPreference = it }
        )

        if (submitState is OnboardingSubmitState.Error) {
            Text("Error: ${(submitState as OnboardingSubmitState.Error).message}")
        }

        if (submitState is OnboardingSubmitState.Loading) {
            CircularProgressIndicator()
        } else {
            Button(onClick = { viewModel.submit() }, modifier = Modifier.fillMaxWidth()) {
                Text("Save preferences")
            }
        }
    }
}

@Composable
private fun LabeledCheckbox(label: String, checked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Checkbox(checked = checked, onCheckedChange = onCheckedChange)
        Text(label)
    }
}

@Composable
private fun LabeledRadioGroup(
    label: String,
    options: List<Pair<String, String>>,
    selected: String,
    onSelect: (String) -> Unit
) {
    Column {
        Text(label)
        options.forEach { (value, displayText) ->
            Row(verticalAlignment = Alignment.CenterVertically) {
                RadioButton(selected = selected == value, onClick = { onSelect(value) })
                Text(displayText)
            }
        }
    }
}