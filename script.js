const scanBtn = document.getElementById('scanBtn');
const targetInput = document.getElementById('targetInput');
const resultBox = document.getElementById('resultBox');

function getSelectedModules() {
  return Array.from(document.querySelectorAll('input[type="checkbox"]'))
    .filter((checkbox) => checkbox.checked)
    .map((checkbox) => checkbox.value);
}

async function runScan() {
  const target = targetInput.value.trim();
  if (!target) {
    resultBox.textContent = 'Please enter a target.';
    return;
  }

  const selectedModules = getSelectedModules();
  resultBox.textContent = 'Running scan...';

  const requestBody = {
    target,
    modules: selectedModules,
    options: {
      mode: 'demo'
    }
  };

  try {
    const response = await fetch('https://httpbin.org/post', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    const data = await response.json();

    resultBox.textContent = JSON.stringify({
      status: 'demo_result',
      target,
      modules: selectedModules,
      request: requestBody,
      response: data
    }, null, 2);
  } catch (error) {
    resultBox.textContent = 'Request failed: ' + error.message;
  }
}

scanBtn.addEventListener('click', runScan);
