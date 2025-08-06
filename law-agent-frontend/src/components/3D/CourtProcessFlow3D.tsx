/**
 * PERFECT 3D Court Process Flow Visualization
 * Advanced React Three Fiber implementation for legal process visualization
 */

import React, { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import {
  Text,
  Box,
  Sphere,
  Line,
  OrbitControls,
  Environment,
  Cylinder,
  Cone
} from '@react-three/drei';
import { Vector3, Color } from 'three';
import * as THREE from 'three';

interface CourtProcessStep {
  id: string;
  title: string;
  description: string;
  position: [number, number, number];
  status: 'pending' | 'active' | 'completed' | 'delayed';
  estimatedDuration: string;
  actualDuration?: string;
  connections: string[];
  legalDomain: string;
}

interface CourtProcessFlow3DProps {
  processType: 'criminal' | 'civil' | 'family' | 'employment';
  currentStep?: string;
  onStepClick?: (stepId: string) => void;
  showTimeline?: boolean;
  animationSpeed?: number;
}

// Perfect 3D Court Process Steps Data
const COURT_PROCESSES: Record<string, CourtProcessStep[]> = {
  criminal: [
    {
      id: 'arrest',
      title: 'Arrest',
      description: 'Police arrest with warrant or probable cause',
      position: [-8, 0, 0],
      status: 'completed',
      estimatedDuration: '1 day',
      actualDuration: '1 day',
      connections: ['booking'],
      legalDomain: 'criminal_law'
    },
    {
      id: 'booking',
      title: 'Booking',
      description: 'Processing at police station',
      position: [-4, 0, 0],
      status: 'completed',
      estimatedDuration: '4-8 hours',
      actualDuration: '6 hours',
      connections: ['arraignment'],
      legalDomain: 'criminal_law'
    },
    {
      id: 'arraignment',
      title: 'Arraignment',
      description: 'First court appearance, plea entered',
      position: [0, 0, 0],
      status: 'active',
      estimatedDuration: '1-3 days',
      connections: ['pretrial', 'plea_bargain'],
      legalDomain: 'criminal_law'
    },
    {
      id: 'plea_bargain',
      title: 'Plea Bargain',
      description: 'Negotiation with prosecutor',
      position: [2, 2, 0],
      status: 'pending',
      estimatedDuration: '2-4 weeks',
      connections: ['sentencing'],
      legalDomain: 'criminal_law'
    },
    {
      id: 'pretrial',
      title: 'Pre-trial',
      description: 'Discovery and motions',
      position: [4, 0, 0],
      status: 'pending',
      estimatedDuration: '3-6 months',
      connections: ['trial'],
      legalDomain: 'criminal_law'
    },
    {
      id: 'trial',
      title: 'Trial',
      description: 'Jury trial or bench trial',
      position: [8, 0, 0],
      status: 'pending',
      estimatedDuration: '1-2 weeks',
      connections: ['sentencing'],
      legalDomain: 'criminal_law'
    },
    {
      id: 'sentencing',
      title: 'Sentencing',
      description: 'Judge determines punishment',
      position: [6, -2, 0],
      status: 'pending',
      estimatedDuration: '2-4 weeks',
      connections: [],
      legalDomain: 'criminal_law'
    }
  ],
  civil: [
    {
      id: 'filing',
      title: 'Filing Complaint',
      description: 'Plaintiff files lawsuit',
      position: [-6, 0, 0],
      status: 'completed',
      estimatedDuration: '1 day',
      connections: ['service'],
      legalDomain: 'civil_law'
    },
    {
      id: 'service',
      title: 'Service of Process',
      description: 'Defendant served with papers',
      position: [-3, 0, 0],
      status: 'completed',
      estimatedDuration: '30 days',
      connections: ['response'],
      legalDomain: 'civil_law'
    },
    {
      id: 'response',
      title: 'Defendant Response',
      description: 'Answer or motion to dismiss',
      position: [0, 0, 0],
      status: 'active',
      estimatedDuration: '30 days',
      connections: ['discovery'],
      legalDomain: 'civil_law'
    },
    {
      id: 'discovery',
      title: 'Discovery Phase',
      description: 'Exchange of evidence',
      position: [3, 0, 0],
      status: 'pending',
      estimatedDuration: '6-12 months',
      connections: ['mediation', 'trial'],
      legalDomain: 'civil_law'
    },
    {
      id: 'mediation',
      title: 'Mediation',
      description: 'Alternative dispute resolution',
      position: [4, 2, 0],
      status: 'pending',
      estimatedDuration: '1-2 days',
      connections: ['settlement'],
      legalDomain: 'civil_law'
    },
    {
      id: 'trial',
      title: 'Trial',
      description: 'Court trial or jury trial',
      position: [6, 0, 0],
      status: 'pending',
      estimatedDuration: '1-5 days',
      connections: ['judgment'],
      legalDomain: 'civil_law'
    },
    {
      id: 'settlement',
      title: 'Settlement',
      description: 'Parties reach agreement',
      position: [6, 2, 0],
      status: 'pending',
      estimatedDuration: '1 day',
      connections: [],
      legalDomain: 'civil_law'
    },
    {
      id: 'judgment',
      title: 'Judgment',
      description: 'Court renders decision',
      position: [8, 0, 0],
      status: 'pending',
      estimatedDuration: '2-4 weeks',
      connections: [],
      legalDomain: 'civil_law'
    }
  ],
  family: [
    {
      id: 'petition',
      title: 'File Petition',
      description: 'Divorce petition filed',
      position: [-6, 0, 0],
      status: 'completed',
      estimatedDuration: '1 day',
      connections: ['service'],
      legalDomain: 'family_law'
    },
    {
      id: 'service',
      title: 'Serve Spouse',
      description: 'Spouse served with papers',
      position: [-3, 0, 0],
      status: 'completed',
      estimatedDuration: '30 days',
      connections: ['response'],
      legalDomain: 'family_law'
    },
    {
      id: 'response',
      title: 'Spouse Response',
      description: 'Response to divorce petition',
      position: [0, 0, 0],
      status: 'active',
      estimatedDuration: '30 days',
      connections: ['temporary_orders', 'discovery'],
      legalDomain: 'family_law'
    },
    {
      id: 'temporary_orders',
      title: 'Temporary Orders',
      description: 'Custody and support orders',
      position: [1, 2, 0],
      status: 'pending',
      estimatedDuration: '2-4 weeks',
      connections: ['discovery'],
      legalDomain: 'family_law'
    },
    {
      id: 'discovery',
      title: 'Financial Discovery',
      description: 'Asset and income disclosure',
      position: [3, 0, 0],
      status: 'pending',
      estimatedDuration: '3-6 months',
      connections: ['mediation', 'trial'],
      legalDomain: 'family_law'
    },
    {
      id: 'mediation',
      title: 'Family Mediation',
      description: 'Custody and property mediation',
      position: [5, 2, 0],
      status: 'pending',
      estimatedDuration: '2-4 sessions',
      connections: ['settlement'],
      legalDomain: 'family_law'
    },
    {
      id: 'trial',
      title: 'Family Court Trial',
      description: 'Judge decides custody/property',
      position: [6, 0, 0],
      status: 'pending',
      estimatedDuration: '1-3 days',
      connections: ['final_decree'],
      legalDomain: 'family_law'
    },
    {
      id: 'settlement',
      title: 'Settlement Agreement',
      description: 'Parties reach agreement',
      position: [7, 2, 0],
      status: 'pending',
      estimatedDuration: '1 day',
      connections: ['final_decree'],
      legalDomain: 'family_law'
    },
    {
      id: 'final_decree',
      title: 'Final Decree',
      description: 'Divorce finalized',
      position: [8, 0, 0],
      status: 'pending',
      estimatedDuration: '2-4 weeks',
      connections: [],
      legalDomain: 'family_law'
    }
  ],
  employment: [
    {
      id: 'incident',
      title: 'Workplace Incident',
      description: 'Discrimination or harassment occurs',
      position: [-6, 0, 0],
      status: 'completed',
      estimatedDuration: '1 day',
      connections: ['internal_complaint'],
      legalDomain: 'employment_law'
    },
    {
      id: 'internal_complaint',
      title: 'Internal Complaint',
      description: 'Report to HR or management',
      position: [-3, 0, 0],
      status: 'completed',
      estimatedDuration: '1-2 weeks',
      connections: ['investigation'],
      legalDomain: 'employment_law'
    },
    {
      id: 'investigation',
      title: 'Company Investigation',
      description: 'Internal investigation process',
      position: [0, 0, 0],
      status: 'active',
      estimatedDuration: '2-4 weeks',
      connections: ['eeoc_filing', 'resolution'],
      legalDomain: 'employment_law'
    },
    {
      id: 'resolution',
      title: 'Internal Resolution',
      description: 'Company resolves internally',
      position: [1, 2, 0],
      status: 'pending',
      estimatedDuration: '1-2 weeks',
      connections: [],
      legalDomain: 'employment_law'
    },
    {
      id: 'eeoc_filing',
      title: 'EEOC Filing',
      description: 'File with Equal Employment Opportunity Commission',
      position: [3, 0, 0],
      status: 'pending',
      estimatedDuration: '180 days from incident',
      connections: ['eeoc_investigation'],
      legalDomain: 'employment_law'
    },
    {
      id: 'eeoc_investigation',
      title: 'EEOC Investigation',
      description: 'Federal investigation',
      position: [6, 0, 0],
      status: 'pending',
      estimatedDuration: '6-12 months',
      connections: ['right_to_sue', 'settlement'],
      legalDomain: 'employment_law'
    },
    {
      id: 'settlement',
      title: 'EEOC Settlement',
      description: 'Settlement through EEOC',
      position: [7, 2, 0],
      status: 'pending',
      estimatedDuration: '2-4 weeks',
      connections: [],
      legalDomain: 'employment_law'
    },
    {
      id: 'right_to_sue',
      title: 'Right to Sue Letter',
      description: 'EEOC issues right to sue',
      position: [9, 0, 0],
      status: 'pending',
      estimatedDuration: '1 week',
      connections: ['lawsuit'],
      legalDomain: 'employment_law'
    },
    {
      id: 'lawsuit',
      title: 'Federal Lawsuit',
      description: 'File lawsuit in federal court',
      position: [12, 0, 0],
      status: 'pending',
      estimatedDuration: '90 days from right to sue',
      connections: [],
      legalDomain: 'employment_law'
    }
  ]
};

// Perfect 3D Step Component
const ProcessStep3D: React.FC<{
  step: CourtProcessStep;
  isActive: boolean;
  onClick: () => void;
  animationOffset: number;
}> = ({ step, isActive, onClick, animationOffset }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Status colors
  const statusColors = {
    completed: '#10B981', // Green
    active: '#3B82F6',    // Blue
    pending: '#6B7280',   // Gray
    delayed: '#EF4444'    // Red
  };

  // Animation
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime + animationOffset) * 0.1;
      meshRef.current.position.y = step.position[1] + Math.sin(state.clock.elapsedTime * 2 + animationOffset) * 0.1;
    }
  });

  return (
    <group position={step.position}>
      {/* Main Step Sphere */}
      <Sphere
        ref={meshRef}
        args={[isActive ? 0.8 : 0.6]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial
          color={statusColors[step.status]}
          emissive={isActive ? statusColors[step.status] : '#000000'}
          emissiveIntensity={isActive ? 0.3 : 0}
          roughness={0.3}
          metalness={0.7}
        />
      </Sphere>

      {/* Status Indicator Ring */}
      {isActive && (
        <Cylinder args={[1.2, 1.2, 0.1, 32]} rotation={[Math.PI / 2, 0, 0]}>
          <meshStandardMaterial
            color={statusColors[step.status]}
            transparent
            opacity={0.3}
            emissive={statusColors[step.status]}
            emissiveIntensity={0.2}
          />
        </Cylinder>
      )}

      {/* Step Title */}
      <Text
        position={[0, -1.5, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        {step.title}
      </Text>

      {/* Duration Info */}
      <Text
        position={[0, -2, 0]}
        fontSize={0.2}
        color="#9CA3AF"
        anchorX="center"
        anchorY="middle"
      >
        {step.estimatedDuration}
      </Text>

      {/* Hover Info Panel - Using Text instead of Html */}
      {hovered && (
        <group position={[0, 2, 0]}>
          <Text
            position={[0, 0.5, 0]}
            fontSize={0.3}
            color="#60A5FA"
            anchorX="center"
            anchorY="middle"
          >
            {step.title}
          </Text>
          <Text
            position={[0, 0, 0]}
            fontSize={0.15}
            color="#E5E7EB"
            anchorX="center"
            anchorY="middle"
          >
            {step.description.length > 50 ? step.description.substring(0, 50) + '...' : step.description}
          </Text>
          <Text
            position={[0, -0.3, 0]}
            fontSize={0.12}
            color={
              step.status === 'completed' ? '#10B981' :
              step.status === 'active' ? '#3B82F6' :
              step.status === 'delayed' ? '#EF4444' : '#9CA3AF'
            }
            anchorX="center"
            anchorY="middle"
          >
            {`Status: ${step.status.toUpperCase()}`}
          </Text>
          <Text
            position={[0, -0.6, 0]}
            fontSize={0.12}
            color="#9CA3AF"
            anchorX="center"
            anchorY="middle"
          >
            {`Duration: ${step.estimatedDuration}`}
          </Text>
        </group>
      )}
    </group>
  );
};

// Perfect Connection Lines Component
const ProcessConnections: React.FC<{
  steps: CourtProcessStep[];
}> = ({ steps }) => {
  const connections = useMemo(() => {
    const lines: Array<{ start: Vector3; end: Vector3; color: string }> = [];
    
    steps.forEach(step => {
      step.connections.forEach(connectionId => {
        const targetStep = steps.find(s => s.id === connectionId);
        if (targetStep) {
          lines.push({
            start: new Vector3(...step.position),
            end: new Vector3(...targetStep.position),
            color: step.status === 'completed' ? '#10B981' : '#6B7280'
          });
        }
      });
    });
    
    return lines;
  }, [steps]);

  return (
    <>
      {connections.map((connection, index) => (
        <Line
          key={index}
          points={[connection.start, connection.end]}
          color={connection.color}
          lineWidth={3}
          transparent
          opacity={0.7}
        />
      ))}
    </>
  );
};

// Main Perfect 3D Court Process Flow Component
const CourtProcessFlow3D: React.FC<CourtProcessFlow3DProps> = ({
  processType,
  currentStep,
  onStepClick,
  showTimeline = true,
  animationSpeed = 1
}) => {
  const [selectedStep, setSelectedStep] = useState<string | null>(currentStep || null);
  const steps = COURT_PROCESSES[processType] || [];

  const handleStepClick = (stepId: string) => {
    setSelectedStep(stepId);
    onStepClick?.(stepId);
  };

  return (
    <>
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        maxDistance={30}
        minDistance={5}
      />

      {/* Perfect Lighting Setup */}
      <ambientLight intensity={0.3} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <pointLight position={[-10, -10, -5]} intensity={0.5} color="#3B82F6" />

      {/* Environment */}
      <Environment preset="night" />

      {/* Process Steps */}
      {steps.map((step, index) => (
        <ProcessStep3D
          key={step.id}
          step={step}
          isActive={selectedStep === step.id}
          onClick={() => handleStepClick(step.id)}
          animationOffset={index * 0.5}
        />
      ))}

      {/* Connection Lines */}
      <ProcessConnections steps={steps} />

      {/* Process Type Title */}
      <Text
        position={[0, 4, 0]}
        fontSize={1}
        color="#3B82F6"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter-bold.woff"
      >
        {processType.replace('_', ' ').toUpperCase()} PROCESS
      </Text>
    </>
  );
};

export default CourtProcessFlow3D;
