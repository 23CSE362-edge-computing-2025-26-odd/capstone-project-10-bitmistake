// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const view = item.dataset.view;
        console.log('Navigating to view:', view); // Debug log
        
        // Update nav
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        // Update views - use a more robust approach
        document.querySelectorAll('.view-container').forEach(v => {
            v.classList.remove('active');
            v.style.display = 'none';
        });
        
        const targetView = document.getElementById(view + 'View');
        
        if (targetView) {
            // Show the target view immediately
            targetView.style.display = 'block';
            targetView.classList.add('active');
            console.log('Successfully activated view:', view + 'View'); // Debug log
            
            // Force a reflow to ensure display change takes effect
            targetView.offsetHeight;
            
            // Clear comparison results when switching to compare view
            if (view === 'compare') {
                const comparisonResults = document.getElementById('comparisonResults');
                const improvementBanner = document.getElementById('improvementBanner');
                if (comparisonResults && !compareData) {
                    // Show empty state if no comparison data
                    comparisonResults.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-icon"></div>
                            <h3>No Comparison Results</h3>
                            <p>Run a comparison to see algorithm performance side by side</p>
                        </div>
                    `;
                }
                if (improvementBanner) {
                    improvementBanner.style.display = 'none';
                }
            }
            
            // Clear chart when switching to analytics view
            if (view === 'analytics') {
                const chartImg = document.getElementById('comparisonChart');
                const placeholder = document.querySelector('.chart-placeholder');
                if (chartImg && placeholder) {
                    chartImg.style.display = 'none';
                    placeholder.style.display = 'block';
                }
            }
            
            // Simple animation without GSAP conflicts
            setTimeout(() => {
                const viewHeader = targetView.querySelector('.view-header');
                const panelCards = targetView.querySelectorAll('.panel-card');
                
                if (viewHeader) {
                    viewHeader.style.opacity = '0';
                    viewHeader.style.transform = 'translateY(-10px)';
                    setTimeout(() => {
                        viewHeader.style.transition = 'all 0.4s ease';
                        viewHeader.style.opacity = '1';
                        viewHeader.style.transform = 'translateY(0)';
                    }, 50);
                }
                
                panelCards.forEach((card, index) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(15px)';
                    setTimeout(() => {
                        card.style.transition = 'all 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100 + (index * 100));
                });
            }, 50);
            
        } else {
            console.error('Could not find view element:', view + 'View'); // Debug log
        }
    });
});

// Slider updates
document.getElementById('singleSensors').addEventListener('input', (e) => {
    document.getElementById('singleSensorsValue').textContent = e.target.value;
});

document.getElementById('singleedgeNodes').addEventListener('input', (e) => {
    document.getElementById('singleedgeValue').textContent = e.target.value;
});

document.getElementById('compareSensors').addEventListener('input', (e) => {
    document.getElementById('compareSensorsValue').textContent = e.target.value;
});

document.getElementById('compareedgeNodes').addEventListener('input', (e) => {
    document.getElementById('compareedgeValue').textContent = e.target.value;
});

// Single Run
let singleData = null;

document.getElementById('runSingle').addEventListener('click', runSingle);

async function runSingle() {
    const button = document.getElementById('runSingle');
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    
    button.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    
    const numSensors = parseInt(document.getElementById('singleSensors').value);
    const numedgeNodes = parseInt(document.getElementById('singleedgeNodes').value);
    const algorithm = document.getElementById('singleAlgorithm').value;
    
    console.log(`Running: ${algorithm}, ${numSensors} sensors, ${numedgeNodes} edge nodes`);
    
    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ numSensors, numedgeNodes, algorithm })
        });
        
        const data = await response.json();
        console.log('Response:', data);
        
        if (data.success) {
            singleData = data;
            displaySingleResults(data);
            drawCanvas('singleCanvas', data);
        } else {
            alert('Simulation failed: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        console.error(error);
    } finally {
        button.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

function displaySingleResults(data) {
    const metricsCard = document.getElementById('singleMetrics');
    const stats = document.getElementById('singleStats');
    
    metricsCard.style.display = 'block';
    stats.style.display = 'flex';
    
    gsap.from(metricsCard, {
        opacity: 0,
        y: 20,
        duration: 0.6,
        ease: 'power3.out'
    });
    
    animateValue('singleLatency', data.metrics.overall_latency);
    animateValue('singleEnergy', data.metrics.energy_consumption);
    animateValue('singleBalance', data.metrics.load_balance_score);
    animateValue('singleNetwork', data.metrics.network_usage);
    
    document.getElementById('singleSensorCount').textContent = data.sensors.length;
    document.getElementById('singleedgeCount').textContent = data.edgeNodes.length;
    document.getElementById('singleLinkCount').textContent = data.assignments.length;
}

function animateValue(id, value) {
    const element = document.getElementById(id);
    const obj = { val: 0 };
    
    gsap.to(obj, {
        val: value,
        duration: 1.5,
        ease: 'power3.out',
        onUpdate: () => {
            element.textContent = obj.val.toFixed(2);
        }
    });
}

function drawCanvas(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas not found: ${canvasId}`);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error(`Could not get 2D context for canvas: ${canvasId}`);
        return;
    }
    
    // Set canvas size explicitly
    const container = canvas.parentElement;
    const containerWidth = container.clientWidth - 40; // Account for padding
    
    // Different sizing for single canvas vs comparison canvases
    let containerHeight;
    if (canvasId === 'singleCanvas') {
        // Single canvas should use full container height
        containerHeight = container.clientHeight - 40;
    } else {
        // Comparison canvases use fixed height
        containerHeight = 280;
    }
    
    canvas.width = containerWidth;
    canvas.height = containerHeight;
    canvas.style.width = containerWidth + 'px';
    canvas.style.height = containerHeight + 'px';
    
    // Clear canvas with proper background
    ctx.fillStyle = '#24181c'; // Background color
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    console.log(`Drawing canvas ${canvasId} with size: ${canvas.width}x${canvas.height}`);
    
    const scaleX = canvas.width / 3000;
    const scaleY = canvas.height / 2000;
    
    // Draw grid (only for larger canvases)
    if (canvasId === 'singleCanvas') {
        ctx.strokeStyle = 'rgba(240, 206, 158, 0.08)';
        ctx.lineWidth = 1;
        const gridSize = Math.min(50, canvas.width / 20);
        for (let x = 0; x < canvas.width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        for (let y = 0; y < canvas.height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }
    }
    
    // Draw connections with better visual quality
    ctx.strokeStyle = 'rgba(240, 206, 158, 0.4)';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    data.assignments.forEach(a => {
        const sensor = data.sensors.find(s => s.id  a.sensorId);
        const edge = data.edgeNodes.find(f => f.id  a.edgeId);
        if (sensor && edge) {
            ctx.beginPath();
            ctx.moveTo(sensor.x * scaleX, sensor.y * scaleY);
            ctx.lineTo(edge.x * scaleX, edge.y * scaleY);
            ctx.stroke();
        }
    });
    
    // Draw edge nodes with better visual quality
    data.edgeNodes.forEach(edge => {
        const x = edge.x * scaleX;
        const y = edge.y * scaleY;
        const size = Math.max(16, Math.min(24, canvas.width / 30));
        
        // Shadow effect
        ctx.shadowColor = 'rgba(240, 206, 158, 0.3)';
        ctx.shadowBlur = 8;
        ctx.shadowOffsetX = 2;
        ctx.shadowOffsetY = 2;
        
        // Main edge node
        ctx.fillStyle = '#d4a574';
        ctx.fillRect(x - size/2, y - size/2, size, size);
        
        // Reset shadow
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        
        // Border
        ctx.strokeStyle = '#f0ce9e';
        ctx.lineWidth = 2;
        ctx.strokeRect(x - size/2, y - size/2, size, size);
        
        // Label
        ctx.fillStyle = '#f0ce9e';
        ctx.font = `${Math.max(10, canvas.width / 40)}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText(`F${edge.id}`, x, y + size/2 + 16);
    });
    
    // Draw sensors with better visual quality
    data.sensors.forEach(sensor => {
        const x = sensor.x * scaleX;
        const y = sensor.y * scaleY;
        const radius = Math.max(6, Math.min(10, canvas.width / 50));
        
        // Shadow effect
        ctx.shadowColor = 'rgba(240, 206, 158, 0.3)';
        ctx.shadowBlur = 6;
        ctx.shadowOffsetX = 1;
        ctx.shadowOffsetY = 1;
        
        // Main sensor circle
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = '#f0ce9e';
        ctx.fill();
        
        // Reset shadow
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        
        // Border
        ctx.strokeStyle = '#e6b88a';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Label
        ctx.fillStyle = '#f0ce9e';
        ctx.font = `${Math.max(8, canvas.width / 60)}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText(`S${sensor.id}`, x, y + radius + 14);
    });
    
    console.log(`Drew ${data.sensors.length} sensors, ${data.edgeNodes.length} edge nodes on canvas ${canvasId}`);
}

// Compare
let compareData = null;

// Animation state management
let isAnimating = false;

document.getElementById('runCompare').addEventListener('click', runCompare);

async function runCompare() {
    const button = document.getElementById('runCompare');
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    
    const checkboxes = document.querySelectorAll('.checkbox-grid input[type="checkbox"]:checked');
    const algorithms = Array.from(checkboxes).map(cb => cb.value);
    
    if (algorithms.length < 2) {
        alert('Please select at least 2 algorithms');
        return;
    }
    
    button.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    
    const numSensors = parseInt(document.getElementById('compareSensors').value);
    const numedgeNodes = parseInt(document.getElementById('compareedgeNodes').value);
    
    console.log(`Comparing: ${algorithms.join(', ')}`);
    
    try {
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ numSensors, numedgeNodes, algorithms })
        });
        
        const data = await response.json();
        console.log('Comparison:', data);
        
        if (data.success) {
            compareData = data;
            displayComparison(data);
        } else {
            alert('Comparison failed: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        console.error(error);
    } finally {
        button.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

function displayComparison(data) {
    const banner = document.getElementById('improvementBanner');
    const label = document.getElementById('improvementLabel');
    const value = document.getElementById('improvementValue');
    const results = document.getElementById('comparisonResults');
    
    banner.style.display = 'block';
    label.textContent = `${data.best_algorithm.toUpperCase()} vs ${data.worst_algorithm.toUpperCase()}:`;
    value.textContent = `${data.improvement >= 0 ? '+' : ''}${data.improvement.toFixed(1)}%`;
    
    results.innerHTML = '';
    
    // Set the data-count attribute for responsive grid layout
    const algorithmCount = Object.keys(data.results).length;
    results.setAttribute('data-count', algorithmCount.toString());
    
    const names = {
        'olb': 'OLB',
        'predictive': 'Predictive',
        'random': 'Random',
        'distance': 'Distance',
        'loadbalanced': 'LoadBalanced',
        'fnpa': 'FNPA'
    };
    
    Object.keys(data.results).forEach((alg, index) => {
        const algData = data.results[alg];
        const card = document.createElement('div');
        card.className = 'result-card';
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        card.innerHTML = `
            <h4>${names[alg] || alg}</h4>
            <canvas class="result-canvas" id="canvas-${alg}"></canvas>
            <div class="result-metrics">
                <div class="result-metric">
                    <span class="result-metric-label">Latency</span>
                    <span class="result-metric-value">${algData.metrics.overall_latency.toFixed(1)}ms</span>
                </div>
                <div class="result-metric">
                    <span class="result-metric-label">Energy</span>
                    <span class="result-metric-value">${algData.metrics.energy_consumption.toFixed(1)}W</span>
                </div>
                <div class="result-metric">
                    <span class="result-metric-label">Balance</span>
                    <span class="result-metric-value">${algData.metrics.load_balance_score.toFixed(3)}</span>
                </div>
                <div class="result-metric">
                    <span class="result-metric-label">Network</span>
                    <span class="result-metric-value">${algData.metrics.network_usage.toFixed(1)}MB/s</span>
                </div>
            </div>
        `;
        results.appendChild(card);
        
        // Animate card appearance
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
        
        // Render canvas after card is visible
        setTimeout(() => {
            const canvas = document.getElementById(`canvas-${alg}`);
            if (canvas) {
                // Ensure canvas is fully rendered before drawing
                requestAnimationFrame(() => {
                    drawCanvas(`canvas-${alg}`, algData);
                });
            }
        }, (index * 100) + 300);
    });
}

// Analytics
document.getElementById('generateChart').addEventListener('click', generateChart);

async function generateChart() {
    const button = document.getElementById('generateChart');
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    
    button.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    
    try {
        const response = await fetch('/api/generate-chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        console.log('Chart response:', data);
        
        if (data.success) {
            const img = document.getElementById('comparisonChart');
            const placeholder = document.querySelector('.chart-placeholder');
            
            img.src = data.chart;
            img.style.display = 'block';
            placeholder.style.display = 'none';
            
            gsap.from(img, {
                opacity: 0,
                scale: 0.95,
                duration: 0.6,
                ease: 'power3.out'
            });
        } else {
            alert('Chart generation failed: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        console.error(error);
    } finally {
        button.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Initial animations - only run once on page load
function runInitialAnimations() {
    // Only animate elements in the active view
    const activeView = document.querySelector('.view-container.active');
    if (activeView) {
        gsap.from(activeView.querySelector('.sidebar'), {
            x: -100,
            opacity: 0,
            duration: 0.8,
            ease: 'power3.out'
        });

        gsap.from(activeView.querySelector('.view-header'), {
            opacity: 0,
            y: -20,
            duration: 0.8,
            delay: 0.2,
            ease: 'power3.out'
        });

        gsap.from(activeView.querySelectorAll('.panel-card'), {
            opacity: 0,
            y: 20,
            duration: 0.8,
            stagger: 0.1,
            delay: 0.3,
            ease: 'power3.out'
        });
    }
}

// Initialize app and check for DOM elements
function initializeApp() {
    console.log('Initializing app...');
    
    // Check if all required elements exist
    const requiredElements = [
        'singleView', 'compareView', 'analyticsView',
        'runSingle', 'runCompare', 'generateChart'
    ];
    
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    
    if (missingElements.length > 0) {
        console.error('Missing required elements:', missingElements);
    } else {
        console.log('All required elements found');
    }
    
    // Ensure single view is active by default
    const singleView = document.getElementById('singleView');
    if (singleView && !singleView.classList.contains('active')) {
        singleView.classList.add('active');
    }
    
    // Run initial animations after a short delay to ensure DOM is ready
    setTimeout(() => {
        runInitialAnimations();
    }, 100);
    
    console.log('App initialized with new UI');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

