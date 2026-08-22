const API_URL = "http://127.0.0.1:8000";


// =====================================================
// SAFE ELEMENT HELPER
// =====================================================

function el(id) {
    return document.getElementById(id);
}


// =====================================================
// NAVIGATION
// =====================================================

function showSection(sectionName) {

    document.querySelectorAll(".section").forEach(section => {
        section.classList.remove("active");
    });

    const section = el(sectionName);

    if (section) {
        section.classList.add("active");
    }

    document.querySelectorAll(".nav-btn").forEach(button => {
        button.classList.remove("active");

        const onclick = button.getAttribute("onclick");

        if (onclick === `showSection('${sectionName}')`) {
            button.classList.add("active");
        }
    });

    const titles = {
        dashboard: "Dashboard",
        servers: "Servers",
        deployments: "Deployments",
        incidents: "Incidents",
        activity: "Activity"
    };

    if (el("page-title")) {
        el("page-title").innerText =
            titles[sectionName] || "OpsPilot";
    }

    if (sectionName === "servers") {
        loadServers();
    }

    if (sectionName === "deployments") {
        loadDeployments();
    }
    if (sectionName === "incidents") {
        loadIncidents();
    }
    if (sectionName === "activity") {
    loadActivities();
}
}


// =====================================================
// LOAD SERVERS
// =====================================================

async function loadServers() {

    try {

        const response = await fetch(
            `${API_URL}/servers`
        );

        if (!response.ok) {
            throw new Error(
                `Server API returned ${response.status}`
            );
        }

        const servers = await response.json();

        console.log("SERVERS:", servers);

        displayServers(servers);
        displayServerHealth(servers);
        updateServerCards(servers);

    } catch (error) {

        console.error(
            "SERVER LOAD ERROR:",
            error
        );

        if (el("serversList")) {
            el("serversList").innerHTML = `
                <div class="empty">
                    Unable to load servers.
                    <br>
                    ${error.message}
                </div>
            `;
        }

        if (el("serverHealth")) {
            el("serverHealth").innerHTML = `
                <div class="empty">
                    Unable to load server health.
                </div>
            `;
        }
    }
}


// =====================================================
// ADD SERVER
// =====================================================

async function addServer() {

    const name =
        el("serverName")?.value.trim();

    const ip =
        el("serverIP")?.value.trim();

    if (!name || !ip) {

        alert(
            "Please enter server name and IP address."
        );

        return;
    }

    try {

        const url =
            `${API_URL}/servers` +
            `?name=${encodeURIComponent(name)}` +
            `&ip_address=${encodeURIComponent(ip)}` +
            `&status=unknown`;

        const response = await fetch(
            url,
            {
                method: "POST"
            }
        );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Failed to add server"
            );
        }

        alert(
            `Server "${data.name}" added successfully!`
        );

        el("serverName").value = "";
        el("serverIP").value = "";

        await loadServers();

    } catch (error) {

        console.error(
            "ADD SERVER ERROR:",
            error
        );

        alert(
            "Failed to add server: " +
            error.message
        );
    }
}


// =====================================================
// DISPLAY SERVERS
// =====================================================

function displayServers(servers) {

    const container =
        el("serversList");

    if (!container) {
        return;
    }

    if (!servers || !servers.length) {

        container.innerHTML = `
            <div class="empty">
                No servers found.
            </div>
        `;

        return;
    }

    container.innerHTML =
        servers.map(server => {

            const status =
                server.status || "unknown";

            const statusClass =
                status.toLowerCase() === "online"
                    ? "online"
                    : "offline";

            const health =
                server.health_status || "unknown";

            return `

                <div class="server-card">

                    <div class="server-top">

                        <div>

                            <div class="server-name">
                                ${server.name || "Unnamed Server"}
                            </div>

                            <div class="deployment-info">
                                ${server.ip_address || "N/A"}
                            </div>

                            <div class="deployment-info">
                                Hostname:
                                ${server.hostname || "N/A"}
                            </div>

                        </div>

                        <div class="${statusClass}">
                            ● ${status}
                        </div>

                    </div>


                    <div class="metrics">

                        <div class="metric">

                            <div class="metric-label">
                                CPU
                            </div>

                            <div class="metric-value">
                                ${server.cpu_usage ?? 0}%
                            </div>

                        </div>


                        <div class="metric">

                            <div class="metric-label">
                                RAM
                            </div>

                            <div class="metric-value">
                                ${server.ram_usage ?? 0}%
                            </div>

                        </div>


                        <div class="metric">

                            <div class="metric-label">
                                Disk
                            </div>

                            <div class="metric-value">
                                ${server.disk_usage ?? 0}%
                            </div>

                        </div>


                        <div class="metric">

                            <div class="metric-label">
                                Health
                            </div>

                            <div class="metric-value">
                                ${health}
                            </div>

                        </div>

                    </div>


                    <div class="deployment-info">

                        Uptime:
                        ${server.uptime || "N/A"}

                        <br>

                        Last Checked:
                        ${server.last_checked || "N/A"}

                    </div>

                </div>

            `;

        }).join("");
}


// =====================================================
// DASHBOARD SERVER HEALTH
// =====================================================

function displayServerHealth(servers) {

    const container =
        el("serverHealth");

    if (!container) {
        return;
    }

    if (!servers || !servers.length) {

        container.innerHTML = `
            <div class="empty">
                No servers available.
            </div>
        `;

        return;
    }

    container.innerHTML =
        servers.map(server => {

            const status =
                server.status || "unknown";

            const statusClass =
                status.toLowerCase() === "online"
                    ? "online"
                    : "offline";

            const health =
                server.health_status || "unknown";

            const healthClass =
                health.toLowerCase() === "healthy"
                    ? "health-good"
                    : "health-bad";

            const cpu =
                Number(server.cpu_usage ?? 0);

            const ram =
                Number(server.ram_usage ?? 0);

            const disk =
                Number(server.disk_usage ?? 0);

            return `

                <div class="server-card">

                    <div class="server-top">

                        <div>

                            <div class="server-name">
                                ${server.name || "Unknown Server"}
                            </div>

                            <div class="deployment-info">
                                ${server.hostname ||
                                server.ip_address ||
                                "N/A"}
                            </div>

                        </div>

                        <div class="${statusClass}">
                            ● ${status.toUpperCase()}
                        </div>

                    </div>


                    <div class="metrics">

                        <!-- CPU -->

                        <div class="metric monitor-metric">

                            <div class="metric-label">
                                CPU
                            </div>

                            <div class="metric-value">
                                ${cpu}%
                            </div>

                            <div class="metric-bar">
                                <div
                                    class="metric-fill"
                                    style="width:${Math.min(cpu, 100)}%"
                                ></div>
                            </div>

                        </div>


                        <!-- RAM -->

                        <div class="metric monitor-metric">

                            <div class="metric-label">
                                RAM
                            </div>

                            <div class="metric-value">
                                ${ram}%
                            </div>

                            <div class="metric-bar">
                                <div
                                    class="metric-fill"
                                    style="width:${Math.min(ram, 100)}%"
                                ></div>
                            </div>

                        </div>


                        <!-- DISK -->

                        <div class="metric monitor-metric">

                            <div class="metric-label">
                                DISK
                            </div>

                            <div class="metric-value">
                                ${disk}%
                            </div>

                            <div class="metric-bar">
                                <div
                                    class="metric-fill"
                                    style="width:${Math.min(disk, 100)}%"
                                ></div>
                            </div>

                        </div>


                        <!-- HEALTH -->

                        <div class="metric monitor-metric">

                            <div class="metric-label">
                                HEALTH
                            </div>

                            <div class="metric-value ${healthClass}">
                                ${health.toUpperCase()}
                            </div>

                        </div>

                    </div>


                    <div class="server-extra">

                        <div>
                            <span>Uptime</span>
                            <strong>
                                ${server.uptime || "N/A"}
                            </strong>
                        </div>

                        <div>
                            <span>Last Checked</span>
                            <strong>
                                ${server.last_checked || "N/A"}
                            </strong>
                        </div>

                    </div>

                </div>

            `;

        }).join("");
}

// =====================================================
// SERVER CARDS
// =====================================================

function updateServerCards(servers) {

    if (el("totalServers")) {

        el("totalServers").innerText =
            servers.length;
    }

    const healthy =
        servers.filter(
            server =>
                server.health_status === "healthy"
        ).length;

    if (el("healthyServers")) {

        el("healthyServers").innerText =
            healthy;
    }
}


// =====================================================
// LOAD DEPLOYMENTS
// =====================================================

async function loadDeployments() {

    try {

        const response = await fetch(
            `${API_URL}/deployments`
        );

        if (!response.ok) {

            throw new Error(
                `Deployment API returned ${response.status}`
            );
        }

        const deployments =
            await response.json();

        console.log(
            "DEPLOYMENTS:",
            deployments
        );

        displayDeployments(deployments);
        displayRecentDeployments(deployments);
        updateDeploymentCards(deployments);

    } catch (error) {

        console.error(
            "DEPLOYMENT LOAD ERROR:",
            error
        );

        if (el("deploymentsList")) {

            el("deploymentsList").innerHTML = `
                <div class="empty">
                    Unable to load deployments.
                </div>
            `;
        }

        if (el("recentDeployments")) {

            el("recentDeployments").innerHTML = `
                <div class="empty">
                    Unable to load deployments.
                </div>
            `;
        }
    }
}
// =====================================================
// LOAD DOCKER
// =====================================================

async function loadDocker() {

    try {

        const response = await fetch(
            `${API_URL}/servers/1/docker`
        );

        if (!response.ok) {
            throw new Error(
                `Docker API returned ${response.status}`
            );
        }

        const data = await response.json();

        console.log("DOCKER:", data);

        displayDocker(data);

    } catch (error) {

        console.error(
            "DOCKER LOAD ERROR:",
            error
        );

        const container = el("dockerInfo");

        if (container) {

            container.innerHTML = `
                <div class="empty">
                    Unable to load Docker information.
                    <br>
                    ${error.message}
                </div>
            `;
        }
    }
}


// =====================================================
// DISPLAY DOCKER
// =====================================================

function displayDocker(data) {

    const container = el("dockerInfo");

    if (!container) {
        return;
    }

    if (!data || data.error) {

        container.innerHTML = `
            <div class="empty">
                Docker information unavailable.
            </div>
        `;

        return;
    }


    // -------------------------------------------------
    // PARSE CONTAINERS
    // -------------------------------------------------

    const containers = (data.containers || "")
        .split("\n")
        .filter(line => line.trim())
        .map(line => {

            try {
                return JSON.parse(line);
            } catch {
                return null;
            }

        })
        .filter(item => item);


    // -------------------------------------------------
    // PARSE IMAGES
    // -------------------------------------------------

    const images = (data.images || "")
        .split("\n")
        .filter(line => line.trim())
        .map(line => {

            try {
                return JSON.parse(line);
            } catch {
                return null;
            }

        })
        .filter(item => item);


    // -------------------------------------------------
    // CONTAINER COUNTS
    // -------------------------------------------------

    const runningContainers =
        containers.filter(
            item =>
                item.State &&
                item.State.toLowerCase() === "running"
        ).length;

    const stoppedContainers =
        containers.filter(
            item =>
                item.State &&
                item.State.toLowerCase() !== "running"
        ).length;


    // -------------------------------------------------
    // DOCKER UI
    // -------------------------------------------------

    container.innerHTML = `

        <div class="metrics">

            <div class="metric">

                <div class="metric-label">
                    Docker Version
                </div>

                <div class="metric-value">
                    ${data.docker_version || "N/A"}
                </div>

            </div>


            <div class="metric">

                <div class="metric-label">
                    Total Containers
                </div>

                <div class="metric-value">
                    ${containers.length}
                </div>

            </div>


            <div class="metric">

                <div class="metric-label">
                    Running
                </div>

                <div class="metric-value green">
                    ${runningContainers}
                </div>

            </div>


            <div class="metric">

                <div class="metric-label">
                    Stopped
                </div>

                <div class="metric-value red">
                    ${stoppedContainers}
                </div>

            </div>


            <div class="metric">

                <div class="metric-label">
                    Images
                </div>

                <div class="metric-value">
                    ${images.length}
                </div>

            </div>

        </div>


        <div class="deployment-info">

            Server:
            <strong>
                ${data.server_name || "N/A"}
            </strong>

        </div>


        <!-- CONTAINERS -->

        <div class="docker-list">

            <h3>Containers</h3>

            ${
                containers.length

                ?

                containers.map(item => {

                    const state =
                        item.State || "unknown";

                    const running =
                        state.toLowerCase() === "running";

                    return `

                        <div class="deployment">

                            <div>

                                <div class="deployment-name">

                                    ${item.Names || "Unknown"}

                                </div>

                                <div class="deployment-info">

                                    Image:
                                    ${item.Image || "N/A"}

                                </div>

                                <div class="deployment-info">

                                    Status:
                                    ${item.Status || "N/A"}

                                </div>

                                <div class="deployment-info">

                                    ID:
                                    ${item.ID || "N/A"}

                                </div>

                            </div>


                            <div class="badge ${
                                running
                                ? "badge-success"
                                : "badge-failed"
                            }">

                                ${
                                    running
                                    ? "RUNNING"
                                    : state.toUpperCase()
                                }

                            </div>

                        </div>

                    `;

                }).join("")

                :

                `
                    <div class="empty">
                        No containers found.
                    </div>
                `
            }

        </div>


        <!-- IMAGES -->

        <div class="docker-list">

            <h3>Docker Images</h3>

            ${
                images.length

                ?

                images.map(item => {

                    return `

                        <div class="deployment">

                            <div>

                                <div class="deployment-name">

                                    ${
                                        item.Repository ||
                                        "Unknown"
                                    }:${
                                        item.Tag ||
                                        "latest"
                                    }

                                </div>

                                <div class="deployment-info">

                                    Size:
                                    ${item.Size || "N/A"}

                                </div>

                                <div class="deployment-info">

                                    Containers:
                                    ${item.Containers || "0"}

                                </div>

                            </div>

                        </div>

                    `;

                }).join("")

                :

                `
                    <div class="empty">
                        No Docker images found.
                    </div>
                `
            }

        </div>

    `;
}

// =====================================================
// DISPLAY DEPLOYMENTS
// =====================================================

function displayDeployments(deployments) {

    const container =
        el("deploymentsList");

    if (!container) {
        return;
    }

    if (!deployments || !deployments.length) {

        container.innerHTML = `
            <div class="empty">
                No deployments found.
            </div>
        `;

        return;
    }

    container.innerHTML =
        deployments.map(
            deployment =>
                createDeploymentHTML(
                    deployment
                )
        ).join("");
}


// =====================================================
// RECENT DEPLOYMENTS
// =====================================================

function displayRecentDeployments(deployments) {

    const container =
        el("recentDeployments");

    if (!container) {
        return;
    }

    if (!deployments || !deployments.length) {

        container.innerHTML = `
            <div class="empty">
                No deployments found.
            </div>
        `;

        return;
    }

    const recent =
        deployments.slice(0, 5);

    container.innerHTML =
        recent.map(
            deployment =>
                createDeploymentHTML(
                    deployment
                )
        ).join("");
}


// =====================================================
// DEPLOYMENT HTML
// =====================================================

function createDeploymentHTML(deployment) {

    const deploymentStatus =
        (deployment.status || "pending").toLowerCase();

    // -------------------------------------------------
    // STATUS
    // -------------------------------------------------

    let badgeClass = "badge-pending";
    let statusText = "PENDING";

    if (deploymentStatus === "success") {
        badgeClass = "badge-success";
        statusText = "SUCCESS";
    }

    else if (deploymentStatus === "failed") {
        badgeClass = "badge-failed";
        statusText = "FAILED";
    }

    else if (deploymentStatus === "running") {
        badgeClass = "badge-running";
        statusText = "RUNNING";
    }


    // -------------------------------------------------
    // DURATION
    // -------------------------------------------------

    let duration = "N/A";

    if (
        deployment.started_at &&
        deployment.completed_at
    ) {

        const start =
            new Date(deployment.started_at);

        const end =
            new Date(deployment.completed_at);

        const seconds =
            Math.max(
                0,
                Math.floor(
                    (end - start) / 1000
                )
            );

        const minutes =
            Math.floor(seconds / 60);

        const remainingSeconds =
            seconds % 60;

        duration =
            `${minutes}m ${remainingSeconds}s`;
    }


    // -------------------------------------------------
    // EXECUTE BUTTON
    // -------------------------------------------------

    let executeButton = "";

    if (deploymentStatus === "running") {

        executeButton = `
            <button
                class="deployment-action deployment-running-btn"
                disabled
            >
                ● Deployment Running...
            </button>
        `;
    }

    else if (
        deploymentStatus === "pending" ||
        deploymentStatus === "failed"
    ) {

        executeButton = `
            <button
                class="deployment-action"
                onclick="executeDeployment(${deployment.id})"
            >
                ▶ Execute Deployment
            </button>
        `;
    }


    // -------------------------------------------------
    // SUCCESS MESSAGE
    // -------------------------------------------------

    let successMessage = "";

    if (deploymentStatus === "success") {

        successMessage = `
            <div class="deployment-success">
                ✓ Deployment completed successfully.
            </div>
        `;
    }


    // -------------------------------------------------
    // ERROR MESSAGE
    // -------------------------------------------------

    let errorMessage = "";

    if (deploymentStatus === "failed") {

        errorMessage = `
            <div class="deployment-error">
                <strong>Deployment Error</strong>

                <div>
                    ${deployment.error_message ||
                    "Deployment failed without an error message."}
                </div>
            </div>
        `;
    }


    // -------------------------------------------------
    // HTML
    // -------------------------------------------------

    return `

        <div class="deployment deployment-card">

            <div class="deployment-header">

                <div>

                    <div class="deployment-name">
                        ${deployment.application_name ||
                        "Unknown Application"}
                    </div>

                    <div class="deployment-info">
                        Deployment #${deployment.id}
                    </div>

                </div>

                <div class="badge ${badgeClass}">
                    ${statusText}
                </div>

            </div>


            <div class="deployment-details">

                <div class="deployment-info">
                    <strong>Server:</strong>
                    ${deployment.server_name || "N/A"}
                </div>

                <div class="deployment-info">
                    <strong>Branch:</strong>
                    ${deployment.branch || "main"}
                </div>

                <div class="deployment-info">
                    <strong>Repository:</strong>
                    ${deployment.repository_url || "N/A"}
                </div>

                <div class="deployment-info">
                    <strong>Docker Image:</strong>
                    ${deployment.docker_image || "N/A"}
                </div>

                <div class="deployment-info">
                    <strong>Container:</strong>
                    ${deployment.container_name || "N/A"}
                </div>

                <div class="deployment-info">
                    <strong>Port:</strong>
                    ${deployment.port || "N/A"}
                </div>

                <div class="deployment-info">
                    <strong>Started:</strong>
                    ${deployment.started_at || "N/A"}
                </div>

                <div class="deployment-info">
                    <strong>Completed:</strong>
                    ${deployment.completed_at || "N/A"}
                </div>

                <div class="deployment-info">
                    <strong>Duration:</strong>
                    ${duration}
                </div>

            </div>


            ${errorMessage}

            ${successMessage}

            ${executeButton}

        </div>

    `;
}

// =====================================================
// DEPLOYMENT CARDS
// =====================================================

function updateDeploymentCards(
    deployments
) {

    if (el("totalDeployments")) {

        el("totalDeployments").innerText =
            deployments.length;
    }

    const failed =
        deployments.filter(
            deployment =>
                deployment.status === "failed"
        ).length;

    if (el("failedDeployments")) {

        el("failedDeployments").innerText =
            failed;
    }
}
// =====================================================
// CREATE INCIDENT
// =====================================================

async function createIncident() {

    const title =
        el("incidentTitle").value.trim();

    const severity =
        el("incidentSeverity").value;

    const description =
        el("incidentDescription").value.trim();

    if (!title) {

        alert("Please enter incident title.");

        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/incidents?server_id=1&title=${encodeURIComponent(title)}&severity=${encodeURIComponent(severity)}&description=${encodeURIComponent(description)}`,
            {
                method: "POST"
            }
        );

        const data =
            await response.json();

        console.log(
            "CREATE INCIDENT:",
            data
        );

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Failed to create incident"
            );
        }

        alert(
            "Incident created successfully!"
        );

        el("incidentTitle").value = "";
        el("incidentDescription").value = "";

        await loadIncidents();

    } catch (error) {

        console.error(
            "CREATE INCIDENT ERROR:",
            error
        );

        alert(
            "Failed to create incident: " +
            error.message
        );
    }
}
// =====================================================
// LOAD INCIDENTS
// =====================================================

async function loadIncidents() {

    try {

        const response = await fetch(
            `${API_URL}/incidents`
        );

        if (!response.ok) {
            throw new Error(
                `Incident API returned ${response.status}`
            );
        }

        const incidents = await response.json();

        console.log("INCIDENTS:", incidents);

        displayIncidents(incidents);

        // Update Open Incidents card
        const openIncidents =
            incidents.filter(
                incident =>
                    incident.status === "open"
            ).length;

        if (el("openIncidents")) {
            el("openIncidents").innerText =
                openIncidents;
        }

    } catch (error) {

        console.error(
            "INCIDENT LOAD ERROR:",
            error
        );

        if (el("incidentsList")) {
            el("incidentsList").innerHTML =
                `<div class="empty">
                    Unable to load incidents.
                </div>`;
        }

        if (el("openIncidents")) {
            el("openIncidents").innerText = "0";
        }
    }
}


// =====================================================
// DISPLAY INCIDENTS
// =====================================================



function displayIncidents(incidents) {

    const container =
        document.getElementById("incidentsList");

    if (!container) {
        return;
    }

    if (!incidents || !incidents.length) {

        container.innerHTML =
            `<div class="empty">
                No incidents found.
             </div>`;

        return;
    }

    container.innerHTML = incidents.map(incident => {

        let statusClass = "badge-pending";

        if (incident.status === "open") {
            statusClass = "badge-failed";
        }

        if (incident.status === "resolved") {
            statusClass = "badge-success";
        }

        return `
            <div class="deployment">

                <div>

                    <div class="deployment-name">
                        ${incident.title || "Untitled Incident"}
                    </div>

                    <div class="deployment-info">

                        Incident #${incident.id}
                        |
                        Server: ${incident.server_name || "Unknown"}
                        |
                        Severity: ${incident.severity || "Unknown"}

                    </div>

                    <div class="deployment-info">

                        Started:
                        ${incident.started_at || "N/A"}

                        |

                        Resolved:
                        ${incident.resolved_at || "N/A"}

                        |

                        Duration:
                        ${incident.duration || "N/A"}

                    </div>

                    ${
                        incident.description
                        ?
                        `
                        <div class="deployment-info">
                            Description:
                            ${incident.description}
                        </div>
                        `
                        :
                        ""
                    }

                    ${
                        incident.resolution
                        ?
                        `
                        <div class="deployment-info">
                            Resolution:
                            ${incident.resolution}
                        </div>
                        `
                        :
                        ""
                    }

                    ${
                        incident.status === "open"
                        ?
                        `
                        <button
                            class="add-btn"
                            onclick="resolveIncident(${incident.id})"
                        >
                            âœ“ Resolve Incident
                        </button>
                        `
                        :
                        ""
                    }

                </div>

                <div class="badge ${statusClass}">
                    ${(incident.status || "unknown").toUpperCase()}
                </div>

            </div>
        `;

    }).join("");

}
// =====================================================
// RESOLVE INCIDENT
// =====================================================

async function resolveIncident(incidentId) {

    const resolution =
        prompt("Enter incident resolution:");

    if (resolution === null) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/incidents/${incidentId}/resolve?resolution=${encodeURIComponent(resolution)}`,
            {
                method: "PUT"
            }
        );

        if (!response.ok) {

            throw new Error(
                `Resolve API returned ${response.status}`
            );

        }

        const data =
            await response.json();

        console.log(
            "INCIDENT RESOLVED:",
            data
        );

        if (data.error) {

            alert(data.error);
            return;

        }

        alert("Incident resolved successfully!");

        await loadIncidents();
        await loadServers();
        await loadActivities();

    } catch (error) {

        console.error(
            "RESOLVE INCIDENT ERROR:",
            error
        );

        alert(
            "Failed to resolve incident: " +
            error.message
        );
    }
}
// =====================================================
// LOAD ACTIVITIES
// =====================================================

async function loadActivities() {

    try {

        const response = await fetch(
            `${API_URL}/activities`
        );

        if (!response.ok) {
            throw new Error(
                `Activity API returned ${response.status}`
            );
        }

        const activities =
            await response.json();

        console.log("ACTIVITIES:", activities);

        displayActivities(activities);

    } catch (error) {

        console.error(
            "ACTIVITY LOAD ERROR:",
            error
        );

        if (el("activitiesList")) {
            el("activitiesList").innerHTML = `
                <div class="empty">
                    Unable to load activities.
                </div>
            `;
        }
    }
}


// =====================================================
// DISPLAY ACTIVITIES
// =====================================================

function displayActivities(activities) {

    const container =
        el("activitiesList");

    if (!container) {
        return;
    }

    if (!activities || !activities.length) {

        container.innerHTML = `
            <div class="empty">
                No activities found.
            </div>
        `;

        return;
    }

    container.innerHTML =
        activities.map(activity => {

            return `
                <div class="deployment">

                    <div>

                        <div class="deployment-name">
                            ${activity.action || "Activity"}
                        </div>

                        <div class="deployment-info">
                            ${activity.description || "No description"}
                        </div>

                        <div class="deployment-info">
                            Time:
                            ${activity.created_at || activity.timestamp || "N/A"}
                        </div>

                    </div>

                </div>
            `;

        }).join("");
}
// =====================================================
// INITIAL LOAD
// =====================================================

async function initializeDashboard() {

    console.log("OpsPilot frontend started");

    await loadServers();

    await loadDeployments();

    await loadIncidents();

    await loadActivities();

    await loadDocker();
}


// =====================================================
// AUTO REFRESH
// =====================================================

setInterval(() => {

    loadServers();
    loadDeployments();
    loadIncidents();
    loadActivities();
    loadDocker();

}, 30000);

window.addEventListener("DOMContentLoaded", () => {
    console.log("DOM LOADED");
    initializeDashboard();
});
// =====================================================
// CREATE DEPLOYMENT
// =====================================================

async function createDeployment() {

    const applicationName =
        el("deploymentApp")?.value.trim();

    const repositoryUrl =
        el("deploymentRepo")?.value.trim();

    const branch =
        el("deploymentBranch")?.value.trim() || "main";

    const dockerImage =
        el("deploymentImage")?.value.trim();

    const containerName =
        el("deploymentContainer")?.value.trim();

    const port =
        el("deploymentPort")?.value || 8000;


    if (!applicationName || !repositoryUrl) {

        alert(
            "Application name and repository URL are required."
        );

        return;
    }


    try {

        const url =
            `${API_URL}/deployments` +
            `?server_id=1` +
            `&application_name=${encodeURIComponent(applicationName)}` +
            `&repository_url=${encodeURIComponent(repositoryUrl)}` +
            `&branch=${encodeURIComponent(branch)}` +
            `&docker_image=${encodeURIComponent(dockerImage)}` +
            `&container_name=${encodeURIComponent(containerName)}` +
            `&port=${encodeURIComponent(port)}`;


        const response =
            await fetch(url, {
                method: "POST"
            });


        const data =
            await response.json();


        console.log(
            "CREATE DEPLOYMENT:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.error ||
                "Failed to create deployment"
            );
        }


        alert(
            `Deployment #${data.id || ""} created successfully!`
        );


        // Clear form

        el("deploymentApp").value = "";
        el("deploymentRepo").value = "";
        el("deploymentBranch").value = "main";
        el("deploymentImage").value = "";
        el("deploymentContainer").value = "";
        el("deploymentPort").value = "8000";


        // Refresh deployment history

        await loadDeployments();


    } catch (error) {

        console.error(
            "CREATE DEPLOYMENT ERROR:",
            error
        );

        alert(
            "Deployment creation failed: " +
            error.message
        );
    }
}
// =====================================================
// EXECUTE DEPLOYMENT
// =====================================================

async function executeDeployment(deploymentId) {

    if (!confirm(
        `Execute Deployment #${deploymentId}?`
    )) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/deployments/${deploymentId}/execute`,
            {
                method: "POST"
            }
        );

        const data =
            await response.json();

        console.log(
            "EXECUTE DEPLOYMENT:",
            data
        );

        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.error ||
                "Deployment execution failed"
            );
        }

        alert(
            `Deployment #${deploymentId} execution started!`
        );

        await loadDeployments();

    } catch (error) {

        console.error(
            "EXECUTE DEPLOYMENT ERROR:",
            error
        );

        alert(
            "Deployment execution failed: " +
            error.message
        );
    }
}
