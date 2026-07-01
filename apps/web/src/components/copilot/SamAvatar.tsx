/**
 * SamAvatar — Official SAM circular avatar (Epic 4D.1).
 *
 * Single source of truth for the SAM avatar image. Used in AgentProfile,
 * ChatMessage, panel headers, and the conversation sidebar. Changing the
 * image here propagates everywhere automatically.
 *
 * Sizes:
 *   xs  — 28×28  (chat messages)
 *   sm  — 32×32  (compact header, sidebar)
 *   md  — 40×40  (panel headers, mobile compact)
 *   lg  — 64×64  (full AgentProfile desktop)
 */

import samPng from "../../assets/avatars/sam.png";

export type AvatarSize = "xs" | "sm" | "md" | "lg";

interface SamAvatarProps {
  size?: AvatarSize;
  /** Show the soft blue glow ring (default true) */
  glow?: boolean;
  /** Show the status dot */
  statusDot?: boolean;
  /** CSS class additions */
  className?: string;
}

const SIZE_CLASSES: Record<AvatarSize, string> = {
  xs: "w-7 h-7",
  sm: "w-8 h-8",
  md: "w-10 h-10",
  lg: "w-10 h-10 sm:w-16 sm:h-16",
};

const GLOW_CLASSES: Record<AvatarSize, string> = {
  xs: "shadow-[0_0_6px_rgba(43,91,215,0.30)]",
  sm: "shadow-[0_0_8px_rgba(43,91,215,0.30)]",
  md: "shadow-[0_0_10px_rgba(43,91,215,0.35)]",
  lg: "shadow-[0_0_14px_rgba(43,91,215,0.40)]",
};

const DOT_CLASSES: Record<AvatarSize, string> = {
  xs: "w-2 h-2 border",
  sm: "w-2.5 h-2.5 border-2",
  md: "w-3 h-3 border-2",
  lg: "w-3 h-3 sm:w-3.5 sm:h-3.5 border-2",
};

export function SamAvatar({
  size = "sm",
  glow = true,
  statusDot = false,
  className = "",
}: SamAvatarProps) {
  return (
    <div className={["relative flex-shrink-0", className].join(" ")}>
      <img
        src={samPng}
        alt="SAM – Supervisory AI Manager"
        className={[
          SIZE_CLASSES[size],
          "rounded-full object-cover",
          "border-2 border-white",
          glow ? GLOW_CLASSES[size] : "",
          "hover:scale-105 hover:shadow-[0_0_18px_rgba(43,91,215,0.55)]",
          "transition-all duration-200",
        ].join(" ")}
      />
      {statusDot && (
        <span
          className={[
            "absolute bottom-0 right-0 rounded-full bg-green-500",
            "border-white",
            DOT_CLASSES[size],
          ].join(" ")}
          aria-label="Online"
        />
      )}
    </div>
  );
}
