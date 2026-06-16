import { useQuery } from "@tanstack/react-query";
import { commentService } from "@/services/comments";
import type { CommentListParams } from "@/types/comment";

export function useComments(params?: CommentListParams) {
  return useQuery({
    queryKey: ["comments", params],
    queryFn: () => commentService.getAll(params),
  });
}
