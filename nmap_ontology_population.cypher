// 1. Define Constraints and Indexes
CREATE CONSTRAINT IF NOT EXISTS FOR (o:Option) REQUIRE o.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (s:ScanType) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (p:Privilege) REQUIRE p.level IS UNIQUE;

// 2. Create Privilege Nodes
MERGE (root:Privilege {level: 'root', description: 'Requires administrative/root privileges'});
MERGE (user:Privilege {level: 'user', description: 'Can be run by standard users'});

// 3. Create ScanType Nodes
MERGE (syn:ScanType {name: 'SYN Scan', flag: '-sS', description: 'TCP SYN stealth scan'});
MERGE (connect:ScanType {name: 'Connect Scan', flag: '-sT', description: 'TCP connect scan'});
MERGE (udp:ScanType {name: 'UDP Scan', flag: '-sU', description: 'UDP scan'});
MERGE (ack:ScanType {name: 'ACK Scan', flag: '-sA', description: 'TCP ACK scan'});

// 4. Create Option Nodes
MERGE (p_flag:Option {name: '-p', description: 'Port specification'});
MERGE (v_flag:Option {name: '-sV', description: 'Service/version detection'});
MERGE (o_flag:Option {name: '-O', description: 'OS detection'});
MERGE (a_flag:Option {name: '-A', description: 'Aggressive scan (OS, version, scripts, traceroute)'});
MERGE (n_flag:Option {name: '-n', description: 'No DNS resolution'});
MERGE (f_flag:Option {name: '-F', description: 'Fast scan (limited ports)'});

// 5. Define Relationships: PRIVILEGE REQUIREMENTS
MATCH (s:ScanType {flag: '-sS'}), (p:Privilege {level: 'root'}) MERGE (s)-[:NEEDS_PRIVILEGE]->(p);
MATCH (s:ScanType {flag: '-sU'}), (p:Privilege {level: 'root'}) MERGE (s)-[:NEEDS_PRIVILEGE]->(p);
MATCH (o:Option {name: '-O'}), (p:Privilege {level: 'root'}) MERGE (o)-[:NEEDS_PRIVILEGE]->(p);
MATCH (o:Option {name: '-A'}), (p:Privilege {level: 'root'}) MERGE (o)-[:NEEDS_PRIVILEGE]->(p);

// 6. Define Relationships: CONFLICTS
MATCH (s1:ScanType {flag: '-sS'}), (s2:ScanType {flag: '-sT'}) MERGE (s1)-[:CONFLICTS_WITH]->(s2) MERGE (s2)-[:CONFLICTS_WITH]->(s1);
MATCH (s1:ScanType {flag: '-sS'}), (s2:ScanType {flag: '-sU'}) MERGE (s1)-[:CONFLICTS_WITH]->(s2) MERGE (s2)-[:CONFLICTS_WITH]->(s1);

// 7. Define Relationships: DEPENDENCIES
MATCH (o:Option {name: '-sV'}), (s:ScanType {flag: '-sS'}) MERGE (o)-[:WORKS_WITH]->(s);
MATCH (o:Option {name: '-sV'}), (s:ScanType {flag: '-sT'}) MERGE (o)-[:WORKS_WITH]->(s);

// 8. Define Relationships: INTENT MAPPING (for Zero-Shot Generation)
MERGE (i1:Intent {name: 'stealth_scan', description: 'Scan without completing TCP connections'})
MERGE (i1)-[:RESOLVES_TO]->(syn);

MERGE (i2:Intent {name: 'version_detection', description: 'Identify services and their versions'})
MERGE (i2)-[:RESOLVES_TO]->(v_flag);

MERGE (i3:Intent {name: 'os_discovery', description: 'Identify the target operating system'})
MERGE (i3)-[:RESOLVES_TO]->(o_flag);
