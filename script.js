document.getElementById('submit-btn').addEventListener('click', () => {
    const email = document.getElementById('email').value;
    const url = document.getElementById('website-url').value;
  
    if (!email || !url) {
      alert('Please fill in both Email ID and Website URL.');
      return;
    }
  
    alert(`Registration Successful!\nEmail: ${email}\nWebsite URL: ${url}`);
  });
  
  // Example: Dynamically add IPs with their data types
  const ipData = [
    { ip: '203.0.113.10', dataType: 'SSH' },
    { ip: '198.51.100.15', dataType: 'UDP' },
    { ip: '192.168.0.100', dataType: 'HTML' }
  ];
  
  const ipTable = document.getElementById('ip-table');
  const totalMembers = document.getElementById('total-members');
  
  ipData.forEach(data => {
    const row = document.createElement('tr');
    const ipCell = document.createElement('td');
    const typeCell = document.createElement('td');
  
    ipCell.textContent = data.ip;
    typeCell.textContent = data.dataType;
  
    row.appendChild(ipCell);
    row.appendChild(typeCell);
    ipTable.appendChild(row);
  });
  
  // Update total members count
  totalMembers.textContent = ipData.length + 4; // Adding 4 from static IPs
  