/**
 * PERFECT 3D Jurisdictional Maps Visualization
 * Advanced React Three Fiber implementation for legal jurisdiction mapping
 */

import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import {
  Text,
  Box,
  Sphere,
  Cylinder,
  Plane,
  OrbitControls,
  Environment
} from '@react-three/drei';
import * as THREE from 'three';

interface JurisdictionData {
  id: string;
  name: string;
  type: 'federal' | 'state' | 'county' | 'municipal';
  position: [number, number, number];
  boundaries: Array<[number, number]>;
  population: number;
  courts: CourtInfo[];
  legalSpecialties: string[];
  caseLoad: number;
  averageProcessingTime: string;
}

interface CourtInfo {
  id: string;
  name: string;
  type: 'supreme' | 'appellate' | 'district' | 'municipal' | 'family' | 'criminal';
  position: [number, number, number];
  jurisdiction: string[];
  judges: number;
  caseBacklog: number;
}

interface JurisdictionalMap3DProps {
  region: 'india' | 'usa' | 'california' | 'texas' | 'newyork' | 'florida';
  focusJurisdiction?: string;
  showCourts?: boolean;
  showCaseLoad?: boolean;
  onJurisdictionClick?: (jurisdictionId: string) => void;
  onCourtClick?: (courtId: string) => void;
}

// Perfect Jurisdictional Data
const JURISDICTIONS: Record<string, JurisdictionData[]> = {
  india: [
    {
      id: 'supreme_court_india',
      name: 'Supreme Court of India',
      type: 'federal',
      position: [0, 3, 0],
      boundaries: [],
      population: 1380000000,
      courts: [
        {
          id: 'sci',
          name: 'Supreme Court of India',
          type: 'supreme',
          position: [0, 4, 0],
          jurisdiction: ['constitutional', 'civil', 'criminal', 'writ'],
          judges: 34,
          caseBacklog: 70000
        },
        {
          id: 'high_courts',
          name: 'High Courts',
          type: 'appellate',
          position: [0, 3.5, 0],
          jurisdiction: ['state_appeals', 'constitutional', 'civil', 'criminal'],
          judges: 1080,
          caseBacklog: 5800000
        }
      ],
      legalSpecialties: ['constitutional', 'fundamental_rights', 'public_interest', 'commercial'],
      caseLoad: 70000,
      averageProcessingTime: '24 months'
    },
    {
      id: 'delhi',
      name: 'Delhi High Court',
      type: 'state',
      position: [0, 1, 0],
      boundaries: [[76.8, 28.4], [77.3, 28.9]],
      population: 32900000,
      courts: [
        {
          id: 'delhi_hc',
          name: 'Delhi High Court',
          type: 'supreme',
          position: [0, 2, 0],
          jurisdiction: ['civil', 'criminal', 'constitutional', 'commercial'],
          judges: 60,
          caseBacklog: 685000
        },
        {
          id: 'delhi_district',
          name: 'District Courts Delhi',
          type: 'district',
          position: [0, 1.5, 0],
          jurisdiction: ['civil', 'criminal', 'family', 'consumer'],
          judges: 700,
          caseBacklog: 850000
        }
      ],
      legalSpecialties: ['commercial', 'intellectual_property', 'consumer', 'family'],
      caseLoad: 1535000,
      averageProcessingTime: '36 months'
    },
    {
      id: 'mumbai',
      name: 'Bombay High Court',
      type: 'state',
      position: [-4, 0, 0],
      boundaries: [[72.7, 18.8], [73.1, 19.3]],
      population: 125000000,
      courts: [
        {
          id: 'bombay_hc',
          name: 'Bombay High Court',
          type: 'supreme',
          position: [-4, 1, 0],
          jurisdiction: ['civil', 'criminal', 'commercial', 'constitutional'],
          judges: 94,
          caseBacklog: 720000
        },
        {
          id: 'mumbai_sessions',
          name: 'Sessions Courts Mumbai',
          type: 'district',
          position: [-4, 0.5, 0],
          jurisdiction: ['criminal', 'civil'],
          judges: 450,
          caseBacklog: 650000
        }
      ],
      legalSpecialties: ['commercial', 'corporate', 'securities', 'maritime'],
      caseLoad: 1370000,
      averageProcessingTime: '42 months'
    },
    {
      id: 'kolkata',
      name: 'Calcutta High Court',
      type: 'state',
      position: [4, 0, 0],
      boundaries: [[88.2, 22.4], [88.5, 22.7]],
      population: 91000000,
      courts: [
        {
          id: 'calcutta_hc',
          name: 'Calcutta High Court',
          type: 'supreme',
          position: [4, 1, 0],
          jurisdiction: ['civil', 'criminal', 'constitutional', 'admiralty'],
          judges: 72,
          caseBacklog: 520000
        },
        {
          id: 'kolkata_district',
          name: 'District Courts Kolkata',
          type: 'district',
          position: [4, 0.5, 0],
          jurisdiction: ['civil', 'criminal', 'family'],
          judges: 380,
          caseBacklog: 480000
        }
      ],
      legalSpecialties: ['constitutional', 'labor', 'intellectual_property', 'admiralty'],
      caseLoad: 1000000,
      averageProcessingTime: '38 months'
    },
    {
      id: 'chennai',
      name: 'Madras High Court',
      type: 'state',
      position: [0, -2, 0],
      boundaries: [[80.1, 12.8], [80.3, 13.2]],
      population: 77000000,
      courts: [
        {
          id: 'madras_hc',
          name: 'Madras High Court',
          type: 'supreme',
          position: [0, -1, 0],
          jurisdiction: ['civil', 'criminal', 'constitutional', 'commercial'],
          judges: 75,
          caseBacklog: 450000
        },
        {
          id: 'chennai_sessions',
          name: 'Sessions Courts Chennai',
          type: 'district',
          position: [0, -1.5, 0],
          jurisdiction: ['criminal', 'civil'],
          judges: 320,
          caseBacklog: 380000
        }
      ],
      legalSpecialties: ['constitutional', 'commercial', 'environmental', 'cyber_law'],
      caseLoad: 830000,
      averageProcessingTime: '34 months'
    },
    {
      id: 'bangalore',
      name: 'Karnataka High Court',
      type: 'state',
      position: [-2, -2, 0],
      boundaries: [[77.4, 12.8], [77.8, 13.1]],
      population: 67000000,
      courts: [
        {
          id: 'karnataka_hc',
          name: 'Karnataka High Court',
          type: 'supreme',
          position: [-2, -1, 0],
          jurisdiction: ['civil', 'criminal', 'constitutional', 'commercial'],
          judges: 62,
          caseBacklog: 380000
        },
        {
          id: 'bangalore_district',
          name: 'District Courts Bangalore',
          type: 'district',
          position: [-2, -1.5, 0],
          jurisdiction: ['civil', 'criminal', 'family', 'consumer'],
          judges: 280,
          caseBacklog: 320000
        }
      ],
      legalSpecialties: ['technology', 'intellectual_property', 'commercial', 'startup_law'],
      caseLoad: 700000,
      averageProcessingTime: '30 months'
    }
  ],
  usa: [
    {
      id: 'federal',
      name: 'Federal Jurisdiction',
      type: 'federal',
      position: [0, 2, 0],
      boundaries: [],
      population: 331000000,
      courts: [
        {
          id: 'scotus',
          name: 'Supreme Court',
          type: 'supreme',
          position: [0, 3, 0],
          jurisdiction: ['constitutional', 'federal'],
          judges: 9,
          caseBacklog: 7000
        },
        {
          id: 'circuit_courts',
          name: 'Circuit Courts',
          type: 'appellate',
          position: [0, 2.5, 0],
          jurisdiction: ['federal_appeals'],
          judges: 179,
          caseBacklog: 48000
        }
      ],
      legalSpecialties: ['constitutional', 'federal_criminal', 'immigration', 'bankruptcy'],
      caseLoad: 400000,
      averageProcessingTime: '18 months'
    },
    {
      id: 'california',
      name: 'California',
      type: 'state',
      position: [-6, 0, 0],
      boundaries: [[-124.4, 32.5], [-114.1, 42.0]],
      population: 39500000,
      courts: [
        {
          id: 'ca_supreme',
          name: 'CA Supreme Court',
          type: 'supreme',
          position: [-6, 1, 0],
          jurisdiction: ['state_appeals'],
          judges: 7,
          caseBacklog: 4500
        },
        {
          id: 'ca_superior',
          name: 'Superior Courts',
          type: 'district',
          position: [-6, 0.5, 0],
          jurisdiction: ['civil', 'criminal', 'family'],
          judges: 2000,
          caseBacklog: 850000
        }
      ],
      legalSpecialties: ['entertainment', 'tech', 'environmental', 'immigration'],
      caseLoad: 1200000,
      averageProcessingTime: '14 months'
    },
    {
      id: 'texas',
      name: 'Texas',
      type: 'state',
      position: [0, 0, 0],
      boundaries: [[-106.6, 25.8], [-93.5, 36.5]],
      population: 29000000,
      courts: [
        {
          id: 'tx_supreme',
          name: 'TX Supreme Court',
          type: 'supreme',
          position: [0, 1, 0],
          jurisdiction: ['civil_appeals'],
          judges: 9,
          caseBacklog: 3200
        },
        {
          id: 'tx_criminal',
          name: 'TX Court of Criminal Appeals',
          type: 'supreme',
          position: [0.5, 1, 0],
          jurisdiction: ['criminal_appeals'],
          judges: 9,
          caseBacklog: 2800
        }
      ],
      legalSpecialties: ['oil_gas', 'agriculture', 'border_law', 'business'],
      caseLoad: 950000,
      averageProcessingTime: '16 months'
    },
    {
      id: 'newyork',
      name: 'New York',
      type: 'state',
      position: [6, 0, 0],
      boundaries: [[-79.8, 40.5], [-71.9, 45.0]],
      population: 19500000,
      courts: [
        {
          id: 'ny_appeals',
          name: 'NY Court of Appeals',
          type: 'supreme',
          position: [6, 1, 0],
          jurisdiction: ['state_appeals'],
          judges: 7,
          caseBacklog: 1500
        },
        {
          id: 'ny_supreme',
          name: 'NY Supreme Court',
          type: 'district',
          position: [6, 0.5, 0],
          jurisdiction: ['civil', 'criminal'],
          judges: 350,
          caseBacklog: 650000
        }
      ],
      legalSpecialties: ['finance', 'real_estate', 'corporate', 'securities'],
      caseLoad: 800000,
      averageProcessingTime: '12 months'
    },
    {
      id: 'florida',
      name: 'Florida',
      type: 'state',
      position: [3, -3, 0],
      boundaries: [[-87.6, 24.5], [-80.0, 31.0]],
      population: 21500000,
      courts: [
        {
          id: 'fl_supreme',
          name: 'FL Supreme Court',
          type: 'supreme',
          position: [3, -2, 0],
          jurisdiction: ['state_appeals'],
          judges: 7,
          caseBacklog: 2100
        },
        {
          id: 'fl_circuit',
          name: 'Circuit Courts',
          type: 'district',
          position: [3, -2.5, 0],
          jurisdiction: ['felony', 'civil_over_30k'],
          judges: 600,
          caseBacklog: 420000
        }
      ],
      legalSpecialties: ['maritime', 'tourism', 'real_estate', 'elder_law'],
      caseLoad: 650000,
      averageProcessingTime: '15 months'
    }
  ]
};

// Perfect 3D Jurisdiction Component
const Jurisdiction3D: React.FC<{
  jurisdiction: JurisdictionData;
  isActive: boolean;
  showCaseLoad: boolean;
  onClick: () => void;
}> = ({ jurisdiction, isActive, showCaseLoad, onClick }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Type colors
  const typeColors = {
    federal: '#DC2626',    // Red
    state: '#3B82F6',      // Blue
    county: '#10B981',     // Green
    municipal: '#F59E0B'   // Yellow
  };

  // Animation
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.005;
      if (isActive) {
        meshRef.current.position.y = jurisdiction.position[1] + Math.sin(state.clock.elapsedTime * 2) * 0.2;
      }
    }
  });

  // Calculate height based on case load
  const height = showCaseLoad ? Math.max(0.5, (jurisdiction.caseLoad / 1000000) * 3) : 1;

  return (
    <group position={jurisdiction.position}>
      {/* Main Jurisdiction Box */}
      <Box
        ref={meshRef}
        args={[2, height, 2]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial
          color={typeColors[jurisdiction.type]}
          emissive={isActive ? typeColors[jurisdiction.type] : '#000000'}
          emissiveIntensity={isActive ? 0.2 : 0}
          roughness={0.4}
          metalness={0.6}
          transparent
          opacity={hovered ? 0.9 : 0.7}
        />
      </Box>

      {/* Population Indicator */}
      <Cylinder
        args={[1.2, 1.2, 0.1, 16]}
        position={[0, height/2 + 0.2, 0]}
        rotation={[Math.PI / 2, 0, 0]}
      >
        <meshStandardMaterial
          color={typeColors[jurisdiction.type]}
          transparent
          opacity={0.3}
        />
      </Cylinder>

      {/* Jurisdiction Name */}
      <Text
        position={[0, height/2 + 0.8, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        {jurisdiction.name}
      </Text>

      {/* Case Load Info */}
      {showCaseLoad && (
        <Text
          position={[0, height/2 + 0.4, 0]}
          fontSize={0.2}
          color="#9CA3AF"
          anchorX="center"
          anchorY="middle"
        >
          {(jurisdiction.caseLoad / 1000).toFixed(0)}K cases
        </Text>
      )}

      {/* Courts */}
      {jurisdiction.courts.map((court, index) => (
        <Court3D
          key={court.id}
          court={court}
          parentPosition={jurisdiction.position}
          index={index}
        />
      ))}

      {/* Hover Info Panel - Using Text instead of Html */}
      {hovered && (
        <group position={[0, height + 1.5, 0]}>
          <Text
            position={[0, 0.5, 0]}
            fontSize={0.3}
            color="#60A5FA"
            anchorX="center"
            anchorY="middle"
          >
            {jurisdiction.name}
          </Text>
          <Text
            position={[0, 0, 0]}
            fontSize={0.15}
            color="#E5E7EB"
            anchorX="center"
            anchorY="middle"
          >
            {`Type: ${jurisdiction.type} | Pop: ${(jurisdiction.population / 1000000).toFixed(1)}M`}
          </Text>
          <Text
            position={[0, -0.3, 0]}
            fontSize={0.15}
            color="#E5E7EB"
            anchorX="center"
            anchorY="middle"
          >
            {`Cases: ${(jurisdiction.caseLoad / 1000).toFixed(0)}K | Courts: ${jurisdiction.courts.length}`}
          </Text>
          <Text
            position={[0, -0.6, 0]}
            fontSize={0.12}
            color="#9CA3AF"
            anchorX="center"
            anchorY="middle"
          >
            {`Processing: ${jurisdiction.averageProcessingTime}`}
          </Text>
        </group>
      )}
    </group>
  );
};

// Perfect 3D Court Component
const Court3D: React.FC<{
  court: CourtInfo;
  parentPosition: [number, number, number];
  index: number;
}> = ({ court, parentPosition, index }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Court type colors
  const courtColors = {
    supreme: '#DC2626',     // Red
    appellate: '#F59E0B',   // Orange
    district: '#3B82F6',    // Blue
    municipal: '#10B981',   // Green
    family: '#8B5CF6',      // Purple
    criminal: '#EF4444'     // Red
  };

  // Animation
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime + index;
    }
  });

  // Position relative to parent
  const angle = (index / 4) * Math.PI * 2;
  const radius = 1.5;
  const position: [number, number, number] = [
    parentPosition[0] + Math.cos(angle) * radius,
    parentPosition[1] + 0.5,
    parentPosition[2] + Math.sin(angle) * radius
  ];

  return (
    <group position={position}>
      <Sphere
        ref={meshRef}
        args={[0.2]}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial
          color={courtColors[court.type]}
          emissive={courtColors[court.type]}
          emissiveIntensity={0.3}
          roughness={0.2}
          metalness={0.8}
        />
      </Sphere>

      {/* Court Info on Hover - Using Text instead of Html */}
      {hovered && (
        <group position={[0, 0.8, 0]}>
          <Text
            position={[0, 0.3, 0]}
            fontSize={0.2}
            color="#A855F7"
            anchorX="center"
            anchorY="middle"
          >
            {court.name}
          </Text>
          <Text
            position={[0, 0, 0]}
            fontSize={0.12}
            color="#E5E7EB"
            anchorX="center"
            anchorY="middle"
          >
            {`Type: ${court.type} | Judges: ${court.judges}`}
          </Text>
          <Text
            position={[0, -0.2, 0]}
            fontSize={0.12}
            color="#E5E7EB"
            anchorX="center"
            anchorY="middle"
          >
            {`Backlog: ${(court.caseBacklog / 1000).toFixed(1)}K cases`}
          </Text>
        </group>
      )}
    </group>
  );
};

// Main Perfect 3D Jurisdictional Map Component
const JurisdictionalMap3D: React.FC<JurisdictionalMap3DProps> = ({
  region,
  focusJurisdiction,
  showCourts = true,
  showCaseLoad = true,
  onJurisdictionClick,
  onCourtClick
}) => {
  const [selectedJurisdiction, setSelectedJurisdiction] = useState<string | null>(focusJurisdiction || null);
  const jurisdictions = JURISDICTIONS[region] || [];

  const handleJurisdictionClick = (jurisdictionId: string) => {
    setSelectedJurisdiction(jurisdictionId);
    onJurisdictionClick?.(jurisdictionId);
  };

  return (
    <>
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        maxDistance={40}
        minDistance={8}
      />

      {/* Perfect Lighting Setup */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[15, 15, 10]} intensity={1.2} />
      <pointLight position={[-15, 10, -10]} intensity={0.8} color="#3B82F6" />
      <spotLight position={[0, 20, 0]} intensity={0.5} angle={Math.PI / 4} />

      {/* Environment */}
      <Environment preset="night" />

      {/* Base Platform */}
      <Plane args={[30, 20]} rotation={[-Math.PI / 2, 0, 0]} position={[0, -2, 0]}>
        <meshStandardMaterial
          color="#1F2937"
          transparent
          opacity={0.3}
          roughness={0.8}
        />
      </Plane>

      {/* Jurisdictions */}
      {jurisdictions.map((jurisdiction) => (
        <Jurisdiction3D
          key={jurisdiction.id}
          jurisdiction={jurisdiction}
          isActive={selectedJurisdiction === jurisdiction.id}
          showCaseLoad={showCaseLoad}
          onClick={() => handleJurisdictionClick(jurisdiction.id)}
        />
      ))}

      {/* Region Title */}
      <Text
        position={[0, 6, 0]}
        fontSize={1.2}
        color="#3B82F6"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        {region.toUpperCase()} LEGAL JURISDICTIONS
      </Text>

      {/* Legend */}
      <group position={[-12, 4, 0]}>
        <Text
          position={[0, 2, 0]}
          fontSize={0.4}
          color="white"
          anchorX="left"
          anchorY="middle"
        >
          JURISDICTION TYPES
        </Text>

        {/* Federal */}
        <Box args={[0.3, 0.3, 0.3]} position={[0, 1, 0]}>
          <meshStandardMaterial color="#DC2626" />
        </Box>
        <Text position={[0.5, 1, 0]} fontSize={0.25} color="white" anchorX="left">
          Federal
        </Text>

        {/* State */}
        <Box args={[0.3, 0.3, 0.3]} position={[0, 0.5, 0]}>
          <meshStandardMaterial color="#3B82F6" />
        </Box>
        <Text position={[0.5, 0.5, 0]} fontSize={0.25} color="white" anchorX="left">
          State
        </Text>

        {/* County */}
        <Box args={[0.3, 0.3, 0.3]} position={[0, 0, 0]}>
          <meshStandardMaterial color="#10B981" />
        </Box>
        <Text position={[0.5, 0, 0]} fontSize={0.25} color="white" anchorX="left">
          County
        </Text>
      </group>
    </>
  );
};

export default JurisdictionalMap3D;
