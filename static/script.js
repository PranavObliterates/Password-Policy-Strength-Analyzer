let scoreChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    
    // Plaintext Handler
    const plaintextForm = document.getElementById('plaintext-form');
    plaintextForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const passwordInput = document.getElementById('password-input').value;
        const submitBtn = plaintextForm.querySelector('button[type="submit"]');
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Auditing...';
        
        try {
            const response = await fetch('/api/audit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'plaintext', value: passwordInput })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                alert(result.error || 'An error occurred.');
                return;
            }
            
            // Display Results
            document.getElementById('plaintext-result').classList.remove('d-none');
            
            // Update Status
            const statusEl = document.getElementById('plaintext-status');
            statusEl.textContent = result.status;
            statusEl.className = 'fw-bold ';
            
            let chartColor = '#198754'; // success
            if (result.status === 'Weak') {
                statusEl.classList.add('text-danger');
                chartColor = '#dc3545'; // danger
            } else if (result.status === 'Moderate') {
                statusEl.classList.add('text-warning');
                chartColor = '#ffc107'; // warning
            } else {
                statusEl.classList.add('text-success');
            }
            
            // Render Chart
            const ctx = document.getElementById('scoreChart').getContext('2d');
            document.getElementById('score-text').textContent = result.score + '%';
            document.getElementById('score-text').style.color = chartColor;
            
            if (scoreChartInstance) {
                scoreChartInstance.destroy();
            }
            
            scoreChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Score', 'Remaining'],
                    datasets: [{
                        data: [result.score, 100 - result.score],
                        backgroundColor: [chartColor, '#e9ecef'],
                        borderWidth: 0,
                        cutout: '75%'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: false }
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true
                    }
                }
            });
            
            // Update Details
            const detailsList = document.getElementById('plaintext-details');
            detailsList.innerHTML = '';
            result.details.forEach(detail => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex align-items-center';
                
                // Add icon based on content
                let iconClass = 'bi-info-circle text-primary';
                if (detail.toLowerCase().includes('weak') || detail.toLowerCase().includes('less than') || detail.toLowerCase().includes('repetitive')) {
                    iconClass = 'bi-exclamation-triangle-fill text-warning';
                }
                if (detail.toLowerCase().includes('good') || detail.toLowerCase().includes('not found')) {
                    iconClass = 'bi-check-circle-fill text-success';
                }
                if (detail.toLowerCase().includes('extremely weak')) {
                    iconClass = 'bi-x-circle-fill text-danger';
                }
                
                li.innerHTML = `<i class="bi ${iconClass} me-3 fs-5"></i><span>${detail}</span>`;
                detailsList.appendChild(li);
            });
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during auditing.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Audit Policy Strength';
        }
    });

    // Hash Handler
    const hashForm = document.getElementById('hash-form');
    hashForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const hashInput = document.getElementById('hash-input').value;
        const submitBtn = hashForm.querySelector('button[type="submit"]');
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Simulating...';
        
        try {
            const response = await fetch('/api/audit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'hash', value: hashInput })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                alert(result.error || 'An error occurred.');
                return;
            }
            
            // Display Results
            document.getElementById('hash-result').classList.remove('d-none');
            
            // Alert Box
            const alertBox = document.getElementById('hash-alert');
            const alertIcon = document.getElementById('hash-icon');
            const alertText = document.getElementById('hash-alert-text');
            
            alertBox.className = 'alert d-flex align-items-center shadow-sm';
            alertIcon.className = 'bi fs-4 me-3';
            
            if (result.status === 'Error') {
                alertBox.classList.add('alert-warning');
                alertIcon.classList.add('bi-exclamation-triangle');
                alertText.textContent = 'Error: ' + result.details;
            } else if (result.cracked) {
                alertBox.classList.add('alert-danger');
                alertIcon.classList.add('bi-shield-x');
                alertText.textContent = 'VULNERABILITY DETECTED! Hash was cracked.';
            } else {
                alertBox.classList.add('alert-success');
                alertIcon.classList.add('bi-shield-check');
                alertText.textContent = 'SECURE. Hash survived dictionary attack.';
            }
            
            // Update Fields
            document.getElementById('hash-algorithm').textContent = result.algorithm || 'N/A';
            document.getElementById('hash-time').textContent = result.time_taken_sec !== undefined ? result.time_taken_sec + ' seconds' : 'N/A';
            document.getElementById('hash-details').textContent = result.details || '';
            
            const crackedPasswordContainer = document.getElementById('hash-cracked-password-container');
            if (result.cracked) {
                crackedPasswordContainer.classList.remove('d-none');
                document.getElementById('hash-cracked-password').textContent = result.password;
            } else {
                crackedPasswordContainer.classList.add('d-none');
                document.getElementById('hash-cracked-password').textContent = '';
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during simulation.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Simulate Dictionary Attack';
        }
    });

});
