// Import necessary dependencies and functions
import { useState } from "react";
import TextField from "@mui/material/TextField";

// ... (existing imports)

function EmployeeData() {
  // ... (existing code)

  const [homeAddressSuggestions, setHomeAddressSuggestions] = useState([]);

  // Function to search employee home address
  async function searchEmployeeHomeAddress(query) {
    try {
      const response = await fetch(
        `/maps/search_employee_home_address/?query=${query}`
      );
      const data = await response.json();

      if (data.success) {
        const suggestions = data.locations;
        setHomeAddressSuggestions(suggestions);
      } else {
        console.error(
          "Error fetching employee home address suggestions:",
          data.error
        );
      }
    } catch (error) {
      console.error("Error fetching employee home address suggestions:", error);
    }
  }

  // Update the home address input and autocomplete dropdown
  function handleEmployeeHomeAddressChange(event) {
    const query = event.target.value;
    searchEmployeeHomeAddress(query);
  }

  // ... (existing code)

  return (
    <Grid container spacing={2}>
      {/* ... (existing code) */}
      <Grid item xs={12} sm={6}>
        <label htmlFor="home_address" className="form-label">
          Home Address<span className="mandatoryStar">*</span>
        </label>
        <TextField
          type="text"
          className="form-control"
          id="home_address"
          name="home_address"
          placeholder="Enter Home Address"
          onChange={handleEmployeeHomeAddressChange}
        />
        <div id="home_address_error"></div>

        {/* Autocomplete dropdown for home address */}
        <ul>
          {homeAddressSuggestions.map((suggestion, index) => (
            <li
              key={index}
              onClick={() => handleAutocompleteSelection("home", suggestion)}
            >
              {suggestion.name}
            </li>
          ))}
        </ul>
      </Grid>
      {/* ... (existing code) */}
    </Grid>
  );

  // ... (existing code)
}

export default EmployeeData;
