export function truncateDescription(description, maxLength) {
  if (description && description.length > maxLength) {
    return description.substring(0, maxLength) + "...";
  }
  return description || "Pas de description";
}


