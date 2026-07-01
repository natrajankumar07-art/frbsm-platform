import { clsx } from "clsx";
import { X, ChevronLeft, ChevronRight, BookOpen } from "lucide-react";
import { useTour } from "../../context/TourContext";

export function ProductTour() {
  const { isActive, currentStep, totalSteps, step, next, prev, dismiss } = useTour();

  if (!isActive) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center pb-6 sm:items-center pointer-events-none"
      role="dialog"
      aria-modal="true"
      aria-label="Product tour"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 pointer-events-auto"
        onClick={dismiss}
        aria-hidden="true"
      />

      {/* Tour card */}
      <div
        className={clsx(
          "relative pointer-events-auto w-full max-w-md mx-4",
          "rounded-2xl border border-border bg-surface-raised dark:bg-gray-900",
          "shadow-2xl shadow-black/20",
          "animate-in slide-in-from-bottom-4 duration-300"
        )}
        style={{ animation: "slideUp 0.25s ease-out" }}
      >
        {/* Progress bar */}
        <div className="h-1 w-full rounded-t-2xl bg-border overflow-hidden">
          <div
            className="h-full bg-accent transition-all duration-300"
            style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
          />
        </div>

        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between gap-3 mb-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl" role="img" aria-label={step.title}>
                {step.icon}
              </span>
              <div>
                <p className="text-caption text-text-secondary dark:text-gray-400">
                  Step {currentStep + 1} of {totalSteps}
                </p>
                <h3 className="text-heading font-bold text-text-primary dark:text-gray-100">
                  {step.title}
                </h3>
              </div>
            </div>
            <button
              onClick={dismiss}
              className="text-text-secondary hover:text-text-primary dark:hover:text-gray-100 p-1 rounded transition-colors flex-shrink-0"
              aria-label="Dismiss tour"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Content */}
          <p className="text-body text-text-secondary dark:text-gray-300 leading-relaxed mb-6">
            {step.description}
          </p>

          {/* Step dots */}
          <div className="flex items-center justify-center gap-1.5 mb-5">
            {Array.from({ length: totalSteps }).map((_, i) => (
              <div
                key={i}
                className={clsx(
                  "rounded-full transition-all duration-200",
                  i === currentStep
                    ? "w-4 h-2 bg-accent"
                    : i < currentStep
                    ? "w-2 h-2 bg-accent/40"
                    : "w-2 h-2 bg-border"
                )}
              />
            ))}
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <button
              onClick={prev}
              disabled={currentStep === 0}
              className={clsx(
                "flex items-center gap-1 text-body font-medium rounded-lg px-3 py-2 transition-colors",
                currentStep === 0
                  ? "text-text-secondary/30 cursor-not-allowed"
                  : "text-text-secondary hover:text-text-primary hover:bg-border"
              )}
              aria-label="Previous step"
            >
              <ChevronLeft className="h-4 w-4" />
              Back
            </button>

            <button
              onClick={dismiss}
              className="text-caption text-text-secondary/60 hover:text-text-secondary transition-colors"
            >
              Skip tour
            </button>

            <button
              onClick={next}
              className="flex items-center gap-1 text-body font-medium rounded-lg px-4 py-2 bg-accent text-white hover:bg-accent/90 transition-colors"
              aria-label={currentStep === totalSteps - 1 ? "Finish tour" : "Next step"}
            >
              {currentStep === totalSteps - 1 ? "Get started" : "Next"}
              {currentStep < totalSteps - 1 && <ChevronRight className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

export function TourRestartButton() {
  const { restart } = useTour();
  return (
    <button
      onClick={restart}
      className="flex items-center gap-2 text-body text-text-secondary hover:text-text-primary transition-colors"
      title="Restart guided tour"
    >
      <BookOpen className="h-4 w-4" />
      <span>Product Tour</span>
    </button>
  );
}
