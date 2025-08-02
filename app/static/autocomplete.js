const startCityInput = document.getElementById("start_city");
const destCityInput = document.getElementById("destination_city");

async function fetchCities(query, callback) {
    const url = `https://wft-geo-db.p.rapidapi.com/v1/geo/cities?limit=5&namePrefix=${query}`;
    const options = {
        method: 'GET',
        headers: {
            'X-RapidAPI-Key': '6f179adacfmshf3746e3059a6954p142e5cjsn5de57eee32eb',  // ← Replace this
            'X-RapidAPI-Host': 'wft-geo-db.p.rapidapi.com'
        }
    };

    try {
        const response = await fetch(url, options);
        const data = await response.json();
        const cities = data.data.map(city => `${city.city}, ${city.countryCode}`);
        callback(cities);
    } catch (error) {
        console.error('Error fetching cities:', error);
    }
}

function enableAutocomplete(inputElement) {
    inputElement.addEventListener("input", async () => {
        const query = inputElement.value;
        if (query.length < 2) return;

        await fetchCities(query, (suggestions) => {
            let datalist = document.getElementById(inputElement.id + "-list");
            if (!datalist) {
                datalist = document.createElement("datalist");
                datalist.id = inputElement.id + "-list";
                document.body.appendChild(datalist);
                inputElement.setAttribute("list", datalist.id);
            }

            datalist.innerHTML = "";
            suggestions.forEach(city => {
                const option = document.createElement("option");
                option.value = city;
                datalist.appendChild(option);
            });
        });
    });
}

enableAutocomplete(startCityInput);
enableAutocomplete(destCityInput);

fetch('/generate-plan', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    destination: 'Paris',
    days: 5,
    interests: 'art, culture, food'
  })
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    document.getElementById("output").innerText = data.itinerary;
  } else {
    alert("Error: " + data.error);
  }
});

