import React, { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import {
  OrbitControls,
  Text,
  Html,
  Environment,
  Plane,
  Line
} from '@react-three/drei';
import * as THREE from 'three';

interface JurisdictionData {
  id: string;
  name: string;
  position: [number, number, number];
  color: string;
  type: 'federal' | 'state' | 'local';
  caseCount: number;
  description: string;
}

const JurisdictionNode: React.FC<{
  jurisdiction: JurisdictionData;
  isActive: boolean;
  onClick: () => void;
}> = ({ jurisdiction, isActive, onClick }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01;
      const scale = isActive ? 1.3 : hovered ? 1.1 : 1;
      meshRef.current.scale.setScalar(scale);
    }
  });

  const getSize = () => {
    switch (jurisdiction.type) {
      case 'federal': return 0.8;
      case 'state': return 0.6;
      case 'local': return 0.4;
      default: return 0.5;
    }
  };

  return (
    <group position={jurisdiction.position}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[getSize(), 32, 32]} />
        <meshStandardMaterial 
          color={isActive ? '#60a5fa' : jurisdiction.color}
          emissive={isActive || hovered ? '#1e40af' : '#000000'}
          emissiveIntensity={isActive || hovered ? 0.3 : 0}
          transparent
          opacity={0.8}
        />
      </mesh>
      
      <Text
        position={[0, getSize() + 0.5, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        {jurisdiction.name}
      </Text>
      
      <Text
        position={[0, getSize() + 0.2, 0]}
        fontSize={0.15}
        color="#d4af37"
        anchorX="center"
        anchorY="middle"
      >
        {jurisdiction.type.toUpperCase()}
      </Text>
      
      {(hovered || isActive) && (
        <Html position={[0, -getSize() - 1, 0]} center>
          <div className="bg-black/90 text-white p-4 rounded-lg backdrop-blur-sm border border-white/20 max-w-sm">
            <h4 className="font-bold text-lg mb-2">{jurisdiction.name}</h4>
            <p className="text-sm text-gray-300 mb-2">{jurisdiction.description}</p>
            <div className="flex justify-between items-center">
              <span className="text-xs bg-primary-500/20 text-primary-400 px-2 py-1 rounded">
                {jurisdiction.type}
              </span>
              <span className="text-xs text-gray-400">
                {jurisdiction.caseCount} cases
              </span>
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

const ConnectionLine: React.FC<{
  start: [number, number, number];
  end: [number, number, number];
  active: boolean;
}> = ({ start, end, active }) => {
  const points = useMemo(() => {
    const startVec = new THREE.Vector3(...start);
    const endVec = new THREE.Vector3(...end);
    const midPoint = startVec.clone().lerp(endVec, 0.5);
    midPoint.y += 1; // Arc effect
    
    const curve = new THREE.QuadraticBezierCurve3(startVec, midPoint, endVec);
    return curve.getPoints(50);
  }, [start, end]);

  const geometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    return geometry;
  }, [points]);

  return (
    <Line
      points={points}
      color={active ? '#60a5fa' : '#666666'}
      lineWidth={active ? 3 : 1}
      transparent
      opacity={active ? 0.8 : 0.3}
    />
  );
};

const JurisdictionalMap: React.FC = () => {
  const [activeJurisdiction, setActiveJurisdiction] = useState<string | null>(null);
  const [animationPhase, setAnimationPhase] = useState(0);

  const jurisdictions: JurisdictionData[] = useMemo(() => [
    {
      id: 'supreme-court',
      name: 'Supreme Court',
      position: [0, 4, 0],
      color: '#dc2626',
      type: 'federal',
      caseCount: 150,
      description: 'Highest court in the United States, final arbiter of constitutional law'
    },
    {
      id: 'federal-circuit',
      name: 'Federal Circuit',
      position: [-3, 2, 0],
      color: '#2563eb',
      type: 'federal',
      caseCount: 1200,
      description: 'Specialized federal court handling patent, trademark, and federal claims'
    },
    {
      id: 'district-court',
      name: 'District Court',
      position: [3, 2, 0],
      color: '#2563eb',
      type: 'federal',
      caseCount: 3500,
      description: 'Federal trial courts with general jurisdiction'
    },
    {
      id: 'state-supreme',
      name: 'State Supreme',
      position: [-2, 0, 2],
      color: '#16a34a',
      type: 'state',
      caseCount: 800,
      description: 'Highest court in state jurisdiction'
    },
    {
      id: 'state-appellate',
      name: 'State Appellate',
      position: [2, 0, 2],
      color: '#16a34a',
      type: 'state',
      caseCount: 2100,
      description: 'Intermediate appellate courts in state system'
    },
    {
      id: 'superior-court',
      name: 'Superior Court',
      position: [-4, -1, 1],
      color: '#16a34a',
      type: 'state',
      caseCount: 5200,
      description: 'General jurisdiction trial courts'
    },
    {
      id: 'municipal-court',
      name: 'Municipal Court',
      position: [0, -2, 3],
      color: '#ca8a04',
      type: 'local',
      caseCount: 8900,
      description: 'Local courts handling municipal violations and minor offenses'
    },
    {
      id: 'family-court',
      name: 'Family Court',
      position: [4, -1, 1],
      color: '#ca8a04',
      type: 'local',
      caseCount: 3400,
      description: 'Specialized courts for family law matters'
    }
  ], []);

  const connections = useMemo(() => [
    { from: 'supreme-court', to: 'federal-circuit' },
    { from: 'supreme-court', to: 'district-court' },
    { from: 'supreme-court', to: 'state-supreme' },
    { from: 'federal-circuit', to: 'district-court' },
    { from: 'state-supreme', to: 'state-appellate' },
    { from: 'state-appellate', to: 'superior-court' },
    { from: 'state-appellate', to: 'family-court' },
    { from: 'superior-court', to: 'municipal-court' },
  ], []);

  useFrame((state) => {
    const time = state.clock.elapsedTime;
    setAnimationPhase(Math.floor(time * 0.5) % jurisdictions.length);
  });

  const getJurisdictionPosition = (id: string): [number, number, number] => {
    const jurisdiction = jurisdictions.find(j => j.id === id);
    return jurisdiction ? jurisdiction.position : [0, 0, 0];
  };

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
      <spotLight
        position={[0, 10, 5]}
        angle={0.5}
        penumbra={1}
        intensity={1}
        color="#d4af37"
      />

      {/* Environment */}
      <Environment preset="night" />

      {/* Background Grid */}
      <Plane args={[20, 20]} position={[0, -3, -2]} rotation={[-Math.PI / 2, 0, 0]}>
        <meshBasicMaterial 
          color="#1e293b" 
          transparent 
          opacity={0.3}
          wireframe
        />
      </Plane>

      {/* Jurisdiction Nodes */}
      {jurisdictions.map((jurisdiction, index) => (
        <JurisdictionNode
          key={jurisdiction.id}
          jurisdiction={jurisdiction}
          isActive={activeJurisdiction === jurisdiction.id || index === animationPhase}
          onClick={() => setActiveJurisdiction(
            activeJurisdiction === jurisdiction.id ? null : jurisdiction.id
          )}
        />
      ))}

      {/* Connection Lines */}
      {connections.map((connection, index) => (
        <ConnectionLine
          key={`${connection.from}-${connection.to}`}
          start={getJurisdictionPosition(connection.from)}
          end={getJurisdictionPosition(connection.to)}
          active={
            activeJurisdiction === connection.from || 
            activeJurisdiction === connection.to ||
            index <= animationPhase
          }
        />
      ))}

      {/* Legend */}
      <Html position={[-8, 3, 0]} transform>
        <div className="bg-black/80 text-white p-4 rounded-lg backdrop-blur-sm border border-white/20">
          <h3 className="font-bold text-lg mb-3 text-center">Court Hierarchy</h3>
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-600 rounded-full"></div>
              <span className="text-sm">Federal Supreme</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-blue-600 rounded-full"></div>
              <span className="text-sm">Federal Courts</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-600 rounded-full"></div>
              <span className="text-sm">State Courts</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-600 rounded-full"></div>
              <span className="text-sm">Local Courts</span>
            </div>
          </div>
        </div>
      </Html>

      {/* Statistics Panel */}
      <Html position={[8, 3, 0]} transform>
        <div className="bg-black/80 text-white p-4 rounded-lg backdrop-blur-sm border border-white/20">
          <h3 className="font-bold text-lg mb-3 text-center">Case Statistics</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Total Cases:</span>
              <span className="text-primary-400 font-bold">
                {jurisdictions.reduce((sum, j) => sum + j.caseCount, 0).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Federal:</span>
              <span className="text-blue-400">
                {jurisdictions
                  .filter(j => j.type === 'federal')
                  .reduce((sum, j) => sum + j.caseCount, 0)
                  .toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span>State:</span>
              <span className="text-green-400">
                {jurisdictions
                  .filter(j => j.type === 'state')
                  .reduce((sum, j) => sum + j.caseCount, 0)
                  .toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Local:</span>
              <span className="text-yellow-400">
                {jurisdictions
                  .filter(j => j.type === 'local')
                  .reduce((sum, j) => sum + j.caseCount, 0)
                  .toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </Html>

      {/* Title */}
      <Html position={[0, 6, 0]} center>
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-2">
            US Court System Hierarchy
          </h2>
          <p className="text-gray-300 text-sm max-w-2xl">
            Interactive 3D visualization of the American judicial system. 
            Click on courts to explore their jurisdiction and case load.
          </p>
        </div>
      </Html>

      {/* Controls */}
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={8}
        maxDistance={20}
        maxPolarAngle={Math.PI / 2}
      />
    </>
  );
};

export default JurisdictionalMap;
