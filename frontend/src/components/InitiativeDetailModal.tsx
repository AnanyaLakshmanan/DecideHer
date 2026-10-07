import React from 'react';
import { InitiativeCluster } from '../types';
import {
  X,
  Layers,
  FileText,
  AlertTriangle,
  Cpu,
  Users,
  Database,
  Workflow,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';
import { getOpportunityTitle } from '../utils/opportunityTitle';

interface InitiativeDetailModalProps {
  initiative: InitiativeCluster | null;
  onClose: () => void;
}

export const InitiativeDetailModal: React.FC<InitiativeDetailModalProps> = ({
  initiative,
  onClose,
}) => {
  if (!initiative) return null;

  const getRatingBadge = (val: 'High' | 'Medium' | 'Low') => {
    switch (val) {
      case 'High':
        return (
          <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            High
          </span>
        );
      case 'Medium':
        return (
          <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
            Medium
          </span>
        );
      case 'Low':
        return (
          <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
            Low
          </span>
        );
      default:
        return <span>{val}</span>;
    }
  };

  return (
    <div
      id="initiative-detail-modal-backdrop"
      className="fixed inset-0 z-50 bg-stone-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto"
      onClick={onClose}
    >
      <div
        id="initiative-detail-modal-container"
        className="bg-white rounded-2xl max-w-2xl w-full border border-stone-200 shadow-2xl overflow-hidden my-8"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top Header */}
        <div className="p-6 pb-4 border-b border-stone-100 flex items-start justify-between bg-stone-50/70">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold text-stone-500">
                Initiative #{initiative.id} · Cluster {initiative.clusterId}
              </span>
              {initiative.spans3PlusDepts && (
                <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                  <Layers className="w-3 h-3" />
                  <span>Cross-functional (3+ depts)</span>
                </span>
              )}
            </div>
            <h2 className="text-xl font-bold text-[#047857] mt-1">
              {getOpportunityTitle(initiative)}
            </h2>
            <div className="flex items-center gap-1.5 mt-1 text-xs text-stone-600">
              <span className="font-semibold">Departments involved:</span>
              <span>{initiative.departments.join(', ')}</span>
              <span className="text-stone-300">•</span>
              <span className="font-semibold">{initiative.useCasesCount} total use cases</span>
              <span className="text-stone-300">•</span>
              <span className="font-semibold">{initiative.departments.length} departments</span>
            </div>
          </div>

          <button
            id="modal-close-btn"
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white border border-stone-200 hover:bg-stone-100 flex items-center justify-center text-stone-500 hover:text-stone-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          {/* Key Metric Pillars: Impact, Readiness, Evidence */}
          <div className="grid grid-cols-3 gap-3 p-4 rounded-xl bg-stone-50 border border-stone-200 text-center">
            <div>
              <div className="text-[11px] font-semibold text-stone-500 uppercase tracking-wider">
                Impact
              </div>
              <div className="mt-1">{getRatingBadge(initiative.impact)}</div>
            </div>
            <div className="border-x border-stone-200">
              <div className="text-[11px] font-semibold text-stone-500 uppercase tracking-wider">
                Readiness
              </div>
              <div className="mt-1">{getRatingBadge(initiative.readiness)}</div>
            </div>
            <div>
              <div className="text-[11px] font-semibold text-stone-500 uppercase tracking-wider">
                Evidence
              </div>
              <div className="mt-1">{getRatingBadge(initiative.evidence)}</div>
            </div>
          </div>

          {/* Finding statement citing countable facts */}
          <div className="p-4 rounded-xl bg-rose-50/50 border border-rose-200/80">
            <div className="text-xs font-bold text-rose-900 uppercase tracking-wide flex items-center gap-1.5 mb-1">
              <CheckCircle2 className="w-4 h-4 text-rose-700" />
              <span>Evidence-based finding</span>
            </div>
            <p className="text-xs text-stone-800 leading-relaxed font-medium">
              {initiative.findingText}
            </p>
            <div className="mt-2.5 flex flex-wrap gap-1.5">
              {initiative.findingDrivers.map((driver, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded text-[10px] bg-white border border-rose-200 text-stone-700 font-medium"
                >
                  {driver}
                </span>
              ))}
            </div>
          </div>

          {/* Readiness 4-Dimension Matrix (Technology, People, Data, Process) */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-stone-700 mb-2.5">
              Readiness Breakdown (Lowest dimension defines overall rating)
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <div className="p-3 rounded-lg border border-stone-200 bg-white">
                <div className="flex items-center gap-1.5 text-xs text-stone-600 mb-1">
                  <Cpu className="w-3.5 h-3.5 text-stone-500" />
                  <span className="font-semibold">Technology</span>
                </div>
                {getRatingBadge(initiative.readinessBreakdown.technology)}
              </div>
              <div className="p-3 rounded-lg border border-stone-200 bg-white">
                <div className="flex items-center gap-1.5 text-xs text-stone-600 mb-1">
                  <Users className="w-3.5 h-3.5 text-stone-500" />
                  <span className="font-semibold">People</span>
                </div>
                {getRatingBadge(initiative.readinessBreakdown.people)}
              </div>
              <div className="p-3 rounded-lg border border-stone-200 bg-white">
                <div className="flex items-center gap-1.5 text-xs text-stone-600 mb-1">
                  <Database className="w-3.5 h-3.5 text-stone-500" />
                  <span className="font-semibold">Data</span>
                </div>
                {getRatingBadge(initiative.readinessBreakdown.data)}
              </div>
              <div className="p-3 rounded-lg border border-stone-200 bg-white">
                <div className="flex items-center gap-1.5 text-xs text-stone-600 mb-1">
                  <Workflow className="w-3.5 h-3.5 text-stone-500" />
                  <span className="font-semibold">Process</span>
                </div>
                {getRatingBadge(initiative.readinessBreakdown.process)}
              </div>
            </div>
          </div>

          {/* Primary Blocker & System Match */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl border border-stone-200 bg-stone-50/50">
              <div className="font-bold text-stone-800 mb-1 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                <span>Primary Concern</span>
              </div>
              <div className="font-semibold text-rose-800">
                {initiative.primaryBlocker}
              </div>
              <p className="text-[11px] text-stone-500 mt-1">
                From field 19 (What stops you from fixing this today?)
              </p>
            </div>

            <div className="p-3 rounded-xl border border-stone-200 bg-stone-50/50">
              <div className="font-bold text-stone-800 mb-1">
                Owned System Match
              </div>
              <div className="font-semibold text-stone-900">
                {initiative.ownedSystemMatch || 'None identified'}
              </div>
              <p className="text-[11px] text-stone-500 mt-1">
                Identified from IT tools audit & enterprise licensing
              </p>
            </div>
          </div>

          {/* Decision-output fields from the pipeline rule specification */}
          <div className="p-4 rounded-xl border border-stone-200 bg-stone-50/60">
            <h3 className="text-xs font-bold uppercase tracking-wider text-stone-700 mb-3">
              Decision rule trace
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div><span className="text-stone-500">Capability</span><div className="font-semibold">{initiative.capabilityType}</div></div>
              <div><span className="text-stone-500">Data object</span><div className="font-semibold">{initiative.dataObject}</div></div>
              <div><span className="text-stone-500">Impact score</span><div className="font-semibold">{initiative.impactScore}</div></div>
              <div><span className="text-stone-500">Evidence score</span><div className="font-semibold">{initiative.evidenceScore}/10 ({initiative.evidenceConfidenceBand})</div></div>
              <div><span className="text-stone-500">Verdict confidence</span><div className="font-semibold">{initiative.verdictConfidenceScore}/10 ({initiative.verdictConfidenceBand})</div></div>
              <div><span className="text-stone-500">Evidence sufficient</span><div className="font-semibold">{initiative.evidenceSufficient ? 'Yes' : 'No'}</div></div>
              <div><span className="text-stone-500">Owned licence unused</span><div className="font-semibold">{initiative.ownedSystemUnusedFlag}</div></div>
              <div className="col-span-2"><span className="text-stone-500">Readiness sources</span><div className="font-semibold">Technology: {initiative.readinessSource.technology}; People: {initiative.readinessSource.people}; Data: {initiative.readinessSource.data}; Process: {initiative.readinessSource.process}</div></div>
              <div className="col-span-2 sm:col-span-3"><span className="text-stone-500">Readiness cap rule</span><div className="font-semibold">{initiative.readinessCapRule}</div></div>
              <div className="col-span-2 sm:col-span-3"><span className="text-stone-500">Verdict-confidence basis</span><div className="font-semibold">{initiative.verdictConfidenceBasis}</div></div>
            </div>
            {!initiative.evidenceSufficient && initiative.missingEvidence.length > 0 && (
              <div className="mt-3 text-[10px] text-amber-800">
                Missing evidence: {initiative.missingEvidence.join(', ')}
              </div>
            )}
            <div className="mt-3 text-[10px] text-stone-500 break-all">
              Evidence references: {initiative.evidenceRefs.join(', ')}
            </div>
          </div>

          {/* Source submissions */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-stone-700 mb-2 flex items-center justify-between">
              <span>Sample Submissions ({initiative.reports.length})</span>
              <span className="text-[11px] font-normal text-stone-500">
                Traceable to actual employee feedback
              </span>
            </h3>

            <div className="space-y-2.5">
              {initiative.reports.map((rep) => (
                <div
                  key={rep.id}
                  className="p-3 rounded-xl border border-stone-200 bg-white text-xs space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-stone-900">
                      {rep.submitterName} ({rep.role} • {rep.department})
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-stone-100 text-stone-600">
                      {rep.id}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold text-stone-700">Today without AI: </span>
                    <span className="text-stone-600">{rep.whatHappensToday}</span>
                  </div>
                  <div>
                    <span className="font-semibold text-stone-700">Future vision: </span>
                    <span className="text-stone-600">{rep.whyWeWantThis}</span>
                  </div>
                  <div className="flex items-center gap-2 pt-1 text-[10px] text-stone-500 flex-wrap">
                    <span>Task: {rep.taskType}</span>
                    <span>•</span>
                    <span>Freq: {rep.frequency}</span>
                    <span>•</span>
                    <span>Time: {rep.timePerOccurrence}</span>
                    <span>•</span>
                    <span className="text-rose-700 font-semibold">
                      Blocker: {rep.blockedBy}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 pt-2 mt-1 border-t border-stone-100 text-[10px] text-stone-600">
                    <span><b>Submitter ref:</b> {rep.submitterId}</span>
                    <span><b>Cluster:</b> {rep.clusterId}</span>
                    <span><b>Capability:</b> {rep.capabilityType}</span>
                    <span><b>Data object:</b> {rep.dataObject}</span>
                    <span><b>Root cause:</b> {rep.rootCauseStated || 'Not stated'} → {rep.rootCauseDerived}</span>
                    <span><b>Personal data:</b> {rep.personalDataFlag}</span>
                    <span><b>Volume proxy:</b> {rep.volumeProxy}/30</span>
                    <span><b>Reach score:</b> {rep.reachScore}/5</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-stone-50 border-t border-stone-100 flex items-center justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-stone-800 hover:bg-stone-900 text-white text-xs font-semibold shadow-xs"
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
};
