import React, { useRef, useState } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import {
  OrbitControls,
  Text,
  Box,
  Cylinder,
  Environment,
  Html
} from '@react-three/drei';
import * as THREE from 'three';
import TalkingAvatar from './TalkingAvatar';

interface CourtElementProps {
  position: [number, number, number];
  color: string;
  label: string;
  description: string;
  onClick?: () => void;
}

const CourtElement: React.FC<CourtElementProps> = ({ 
  position, 
  color, 
  label, 
  description, 
  onClick 
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const [clicked, setClicked] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01;
      if (hovered) {
        meshRef.current.scale.setScalar(1.1);
      } else {
        meshRef.current.scale.setScalar(1);
      }
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={() => {
          setClicked(!clicked);
          onClick?.();
        }}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial 
          color={hovered ? '#60a5fa' : color} 
          emissive={hovered ? '#1e40af' : '#000000'}
          emissiveIntensity={hovered ? 0.2 : 0}
        />
      </mesh>
      
      <Text
        position={[0, 1.5, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        {label}
      </Text>
      
      {hovered && (
        <Html position={[0, -1.5, 0]} center>
          <div className="bg-black/80 text-white p-3 rounded-lg backdrop-blur-sm border border-white/20 max-w-xs">
            <h4 className="font-semibold text-sm mb-1">{label}</h4>
            <p className="text-xs text-gray-300">{description}</p>
          </div>
        </Html>
      )}
    </group>
  );
};

const JudgeBench: React.FC = () => {
  const meshRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
    }
  });

  return (
    <group ref={meshRef} position={[0, 0, -4]}>
      {/* Judge's Bench */}
      <Box args={[4, 1, 2]} position={[0, 0.5, 0]}>
        <meshStandardMaterial color="#8B4513" />
      </Box>
      
      {/* Judge's Chair */}
      <Box args={[1, 2, 1]} position={[0, 1.5, -0.5]}>
        <meshStandardMaterial color="#654321" />
      </Box>
      
      {/* Gavel */}
      <Cylinder args={[0.05, 0.05, 0.3]} position={[1, 1.2, 0.5]} rotation={[0, 0, Math.PI / 4]}>
        <meshStandardMaterial color="#8B4513" />
      </Cylinder>
      
      <Text
        position={[0, 2.5, 0]}
        fontSize={0.4}
        color="#d4af37"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        JUDGE'S BENCH
      </Text>
    </group>
  );
};

const CourtSeating: React.FC = () => {
  const seats = [];
  
  // Create jury box
  for (let i = 0; i < 12; i++) {
    const x = (i % 4) * 0.8 - 1.2;
    const z = Math.floor(i / 4) * 0.8 + 2;
    seats.push(
      <Box key={`jury-${i}`} args={[0.6, 0.6, 0.6]} position={[x, 0.3, z]}>
        <meshStandardMaterial color="#4169E1" />
      </Box>
    );
  }
  
  // Create gallery seating
  for (let row = 0; row < 5; row++) {
    for (let seat = 0; seat < 8; seat++) {
      const x = seat * 0.8 - 2.8;
      const z = row * 0.8 + 5;
      seats.push(
        <Box key={`gallery-${row}-${seat}`} args={[0.6, 0.6, 0.6]} position={[x, 0.3, z]}>
          <meshStandardMaterial color="#8B4513" />
        </Box>
      );
    }
  }
  
  return <group>{seats}</group>;
};

const LegalProcessFlow: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  
  const steps = [
    { label: "Filing", position: [-6, 2, 0] as [number, number, number], color: "#ef4444", description: "Initial case filing and documentation" },
    { label: "Discovery", position: [-3, 2, 0] as [number, number, number], color: "#f59e0b", description: "Evidence gathering and investigation" },
    { label: "Motions", position: [0, 2, 0] as [number, number, number], color: "#eab308", description: "Pre-trial motions and hearings" },
    { label: "Trial", position: [3, 2, 0] as [number, number, number], color: "#22c55e", description: "Court proceedings and testimony" },
    { label: "Verdict", position: [6, 2, 0] as [number, number, number], color: "#3b82f6", description: "Final decision and judgment" },
  ];

  useFrame((state) => {
    const time = state.clock.elapsedTime;
    setActiveStep(Math.floor(time % steps.length));
  });

  return (
    <group>
      {steps.map((step, index) => (
        <CourtElement
          key={step.label}
          position={step.position}
          color={index === activeStep ? step.color : '#666666'}
          label={step.label}
          description={step.description}
        />
      ))}
      
      {/* Connection lines */}
      {steps.slice(0, -1).map((step, index) => (
        <mesh key={`line-${index}`} position={[step.position[0] + 1.5, 2, 0]}>
          <cylinderGeometry args={[0.02, 0.02, 3]} />
          <meshStandardMaterial 
            color={index <= activeStep ? '#60a5fa' : '#666666'} 
            emissive={index <= activeStep ? '#1e40af' : '#000000'}
            emissiveIntensity={0.3}
          />
        </mesh>
      ))}
      
      <Text
        position={[0, 4, 0]}
        fontSize={0.6}
        color="#d4af37"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        LEGAL PROCESS FLOW
      </Text>
    </group>
  );
};

const CourtVisualization: React.FC = () => {
  
  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
      <spotLight
        position={[0, 15, 0]}
        angle={0.3}
        penumbra={1}
        intensity={1}
        castShadow
        color="#d4af37"
      />

      {/* Environment */}
      <Environment preset="city" />

      {/* Court Floor */}
      <mesh position={[0, -0.5, 0]} receiveShadow>
        <boxGeometry args={[20, 0.1, 15]} />
        <meshStandardMaterial color="#2c1810" />
      </mesh>

      {/* Court Walls */}
      <mesh position={[0, 3, -7.5]}>
        <boxGeometry args={[20, 6, 0.2]} />
        <meshStandardMaterial color="#8B4513" />
      </mesh>

      {/* Judge's Area */}
      <JudgeBench />

      {/* Seating */}
      <CourtSeating />

      {/* Legal Process Visualization */}
      <LegalProcessFlow />

      {/* Lawyer Tables */}
      <Box args={[3, 0.8, 1.5]} position={[-2, 0.4, 1]}>
        <meshStandardMaterial color="#654321" />
      </Box>
      <Box args={[3, 0.8, 1.5]} position={[2, 0.4, 1]}>
        <meshStandardMaterial color="#654321" />
      </Box>

      {/* Witness Stand */}
      <group position={[4, 0, -1]}>
        <Box args={[1.5, 0.8, 1.5]} position={[0, 0.4, 0]}>
          <meshStandardMaterial color="#8B4513" />
        </Box>
        <Box args={[0.8, 1.5, 0.8]} position={[0, 1.15, -0.35]}>
          <meshStandardMaterial color="#654321" />
        </Box>
        <Text
          position={[0, 2, 0]}
          fontSize={0.3}
          color="#d4af37"
          anchorX="center"
          anchorY="middle"
        >
          WITNESS STAND
        </Text>
      </group>

      {/* Court Reporter */}
      <group position={[-4, 0, -1]}>
        <Box args={[1, 0.6, 1]} position={[0, 0.3, 0]}>
          <meshStandardMaterial color="#4169E1" />
        </Box>
        <Text
          position={[0, 1.2, 0]}
          fontSize={0.25}
          color="white"
          anchorX="center"
          anchorY="middle"
        >
          COURT REPORTER
        </Text>
      </group>

      {/* Talking Avatar - Legal Assistant */}
      <TalkingAvatar
        position={[4, 1, 2]}
        scale={1.2}
        onSpeak={(message) => {
          console.log('Avatar speaking:', message);
          // Add speech synthesis for the talking avatar
          if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(message);
            const voices = speechSynthesis.getVoices();
            utterance.voice = voices.find(voice =>
              voice.name.includes('Female') || voice.name.includes('female')
            ) || voices[0];
            utterance.rate = 0.9;
            utterance.pitch = 1.1;
            speechSynthesis.speak(utterance);
          }
        }}
      />

      {/* Interactive Elements */}
      <Html position={[0, 6, 0]} center>
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-2">3D Court Visualization</h2>
          <p className="text-gray-300 text-sm max-w-md">
            Explore the courtroom layout and legal process flow.
            Click on the legal assistant avatar to interact with her!
          </p>
        </div>
      </Html>

      {/* Controls */}
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={25}
        maxPolarAngle={Math.PI / 2}
      />
    </>
  );
};

export default CourtVisualization;
