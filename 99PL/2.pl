second_last(X, [X,_]).
second_last(X, [_|T]) :- second_last(X,T).
