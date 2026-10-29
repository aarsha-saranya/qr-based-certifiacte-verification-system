const result = document.getElementById("result");
const idBox = document.getElementById("cert-id");
const id = String(window.CERTIFICATE_ID || "").trim();
idBox.textContent = id || "Missing certificate ID";

function show(kind, title, fields) {
  result.className = `result ${kind}`;
  result.replaceChildren();
  const heading = document.createElement("h3");
  heading.textContent = title;
  result.appendChild(heading);
  fields.forEach(([label, value]) => {
    const p = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${label}: `;
    p.append(strong, document.createTextNode(value || "Not provided"));
    result.appendChild(p);
  });
}

async function verify() {
  if (!id) {
    show("invalid", "✕ Invalid verification link", [["Details", "No certificate ID was included in this link."]]);
    return;
  }
  try {
    const response = await fetch(`/certificates/${encodeURIComponent(id)}`);
    const data = await response.json();
    if (response.status === 404) {
      show("invalid", "✕ Certificate not found", [["Result", "No matching record was found. Check the certificate ID."]]);
      return;
    }
    if (!response.ok) throw new Error("The verification service could not complete the request.");
    const status = String(data.status || "valid").toLowerCase();
    if (status === "revoked") {
      show("invalid", "✕ Certificate revoked", [["Status", "The institution has marked this certificate as revoked."], ["Certificate ID", id]]);
      return;
    }
    if (!["valid", "active"].includes(status)) {
      show("invalid", "Certificate status needs review", [["Status", status], ["Certificate ID", id]]);
      return;
    }
    show("success", "✓ Certificate record verified", [
      ["Student", data.name],
      ["Course / workshop", data.course_name],
      ["Institution", data.issued_by],
      ["Certificate ID", data.certificate_id || id],
      ["Issue date", data.issue_date]
    ]);
  } catch (error) {
    show("warning", "Verification temporarily unavailable", [["Reason", "The server could not be reached. Please try again later."]]);
  }
}
verify();
